"""In-process search over the bundled BNHS knowledge base.

The corpus (backend/data/knowledge_base.json.gz, built by
scripts/build_knowledge_base.py from the public BNHS collections API) is
small enough to index in memory at startup: ~3,000 documents, ~130 KB
compressed. Ranking is BM25 over title, tags and body with field weights, plus
a boost when the whole query appears in the title -- no embedding model or
database round-trip needed, so search works offline and in tests.
"""

from __future__ import annotations

import gzip
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base.json.gz"

FIELD_WEIGHTS = {"title": 3.0, "tags": 1.5, "content": 1.0}
BM25_K1 = 1.2
BM25_B = 0.75

STOPWORDS = frozenset(
    """a an and are as at be by can do does for from has have how i in is it its of on or
    that the their there these this to was were what when where which who why will with
    about into than then them they you your me my we our tell show find give list any some""".split()
)

SOURCE_LABELS = {
    "species": "Species record",
    "field_guide": "Field guide",
    "hornbill": "Hornbill magazine",
    "buceros": "Buceros (ENVIS newsletter)",
    "newsletter": "BNHS newsletter",
    "jbnhs": "JBNHS journal",
    "publication": "BNHS publication",
    "collector": "Collector profile",
    "bnhs_programme": "BNHS programme",
}


def tokenize(text: str) -> list[str]:
    tokens = []
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        if word in STOPWORDS or len(word) < 2:
            continue
        # Light plural folding so "vultures" finds "vulture".
        if len(word) > 4 and word.endswith("ies"):
            word = word[:-3] + "y"
        elif len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        tokens.append(word)
    return tokens


@dataclass(eq=False)
class Document:
    id: str
    source_type: str
    title: str
    content: str
    url: str | None
    author: str | None
    date: str | None
    tags: list[str]
    term_freqs: dict[str, Counter] = field(default_factory=dict, repr=False)
    lengths: dict[str, int] = field(default_factory=dict, repr=False)

    @property
    def content_type(self) -> str:
        return SOURCE_LABELS.get(self.source_type, self.source_type.replace("_", " ").title())

    def summary(self, limit: int = 300) -> str:
        text = re.sub(r"\s+", " ", self.content).strip()
        return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


@dataclass
class SearchHit:
    document: Document
    score: float
    similarity: float


class KnowledgeBase:
    def __init__(self, documents: list[dict]):
        self.documents: list[Document] = []
        self.postings: dict[str, list[int]] = defaultdict(list)
        self.avg_lengths: dict[str, float] = {}
        totals = Counter()

        for index, raw in enumerate(documents):
            doc = Document(
                id=raw["id"],
                source_type=raw.get("source_type", "document"),
                title=raw.get("title") or "Untitled",
                content=raw.get("content") or "",
                url=raw.get("url"),
                author=raw.get("author"),
                date=raw.get("date"),
                tags=raw.get("tags") or [],
            )
            fields = {"title": doc.title, "tags": " ".join(doc.tags), "content": doc.content}
            seen: set[str] = set()
            for name, text in fields.items():
                tokens = tokenize(text)
                doc.term_freqs[name] = Counter(tokens)
                doc.lengths[name] = len(tokens)
                totals[name] += len(tokens)
                seen.update(tokens)
            for term in seen:
                self.postings[term].append(index)
            self.documents.append(doc)

        count = max(len(self.documents), 1)
        self.avg_lengths = {name: max(totals[name] / count, 1.0) for name in FIELD_WEIGHTS}
        self.by_id = {doc.id: doc for doc in self.documents}

    def _idf(self, term: str) -> float:
        df = len(self.postings.get(term, ()))
        n = len(self.documents)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def search(
        self, query: str, limit: int = 10, source_types: set[str] | None = None
    ) -> list[SearchHit]:
        terms = list(dict.fromkeys(tokenize(query)))
        if not terms:
            return []

        candidates: set[int] = set()
        for term in terms:
            candidates.update(self.postings.get(term, ()))

        phrase = " ".join(terms)
        idfs = {term: self._idf(term) for term in terms}
        scored: list[tuple[float, float, int]] = []
        for index in candidates:
            doc = self.documents[index]
            if source_types and doc.source_type not in source_types:
                continue
            score = 0.0
            matched = 0
            for term in terms:
                term_score = 0.0
                for name, weight in FIELD_WEIGHTS.items():
                    tf = doc.term_freqs[name].get(term, 0)
                    if not tf:
                        continue
                    norm = 1 - BM25_B + BM25_B * doc.lengths[name] / self.avg_lengths[name]
                    term_score += weight * tf * (BM25_K1 + 1) / (tf + BM25_K1 * norm)
                if term_score:
                    matched += 1
                    score += idfs[term] * term_score
            if phrase and phrase in " ".join(tokenize(doc.title)):
                score *= 1.5
            coverage = matched / len(terms)
            # Prefer documents that match every query word over ones that
            # repeat a single word many times.
            score *= 0.5 + 0.5 * coverage
            scored.append((score, coverage, index))

        if not scored:
            return []
        scored.sort(key=lambda item: item[0], reverse=True)
        top_score = scored[0][0]
        hits = []
        for score, coverage, index in scored[:limit]:
            similarity = round(0.6 * coverage + 0.4 * (score / top_score), 4)
            hits.append(SearchHit(self.documents[index], score, similarity))
        return hits

    def of_type(self, *source_types: str) -> list[Document]:
        return [doc for doc in self.documents if doc.source_type in source_types]


@lru_cache
def get_knowledge_base() -> KnowledgeBase:
    if not DATA_FILE.exists():
        return KnowledgeBase([])
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as handle:
        return KnowledgeBase(json.load(handle))


def search(query: str, limit: int = 10, source_types: set[str] | None = None) -> list[SearchHit]:
    return get_knowledge_base().search(query, limit=limit, source_types=source_types)
