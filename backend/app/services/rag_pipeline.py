"""End-to-end RAG pipeline.

Retrieval: BM25 over the bundled BNHS knowledge base (app.services.knowledge_base).

Generation (next-steps, quiz, ask): Groq's OpenAI-compatible chat completions
API, in JSON mode, grounded in the retrieved documents. Every generator has a
deterministic fallback built from the same documents, so the Knowledge Hub,
the daily question and the chatbot keep working when GROQ_API_KEY is unset,
the quota runs out, or the model returns something malformed.
"""

from __future__ import annotations

import json
import logging
import random
import re
from datetime import date
from functools import lru_cache

from app.core.config import get_settings
from app.models.schema import (
    AskRequest,
    AskResponse,
    AskSource,
    NextStepAction,
    NextStepsQuery,
    NextStepsResponse,
    QuizQuery,
    QuizQuestion,
    QuizResponse,
    SearchQuery,
    SearchResponse,
    SearchResultCard,
)
from app.services import knowledge_base
from app.services.knowledge_base import Document

logger = logging.getLogger(__name__)

GROQ_MODEL = "openai/gpt-oss-120b"
LLM_TIMEOUT_SECONDS = 30

# Map the free-text filter the API accepts onto the corpus' source types.
FILTER_ALIASES = {
    "species": {"species", "field_guide"},
    "birds": {"field_guide", "species"},
    "publications": {"hornbill", "buceros", "newsletter", "jbnhs", "publication"},
    "people": {"collector"},
    "programmes": {"bnhs_programme"},
}


class LLMUnavailable(Exception):
    pass


@lru_cache
def get_groq_client():
    settings = get_settings()
    if not settings.groq_api_key:
        raise LLMUnavailable("GROQ_API_KEY is not set")
    from groq import Groq

    return Groq(api_key=settings.groq_api_key, timeout=LLM_TIMEOUT_SECONDS, max_retries=1)


def _generate_json(system: str, prompt: str) -> dict:
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except LLMUnavailable:
        raise
    except Exception as exc:  # network, quota, auth, malformed JSON
        logger.warning("LLM call failed, using archive fallback: %s", exc)
        raise LLMUnavailable(str(exc)) from exc


def _context_block(documents: list[Document], chars: int = 600) -> str:
    return "\n\n".join(
        f"[{index}] ({doc.content_type}) {doc.title}\n{doc.summary(chars)}"
        for index, doc in enumerate(documents, start=1)
    )


# ---------------------------------------------------------------------------
# 1. Search
# ---------------------------------------------------------------------------


def search_resources(body: SearchQuery) -> SearchResponse:
    source_types = FILTER_ALIASES.get((body.filter_type or "").lower())
    hits = knowledge_base.search(body.query, limit=body.limit, source_types=source_types)
    return SearchResponse(
        results=[
            SearchResultCard(
                id=hit.document.id,
                title=hit.document.title,
                summary=hit.document.summary(),
                content_type=hit.document.content_type,
                source="BNHS",
                image_url=None,
                bnhs_url=hit.document.url,
                file_name=None,
                author=hit.document.author,
                similarity_score=hit.similarity,
            )
            for hit in hits
        ]
    )


# ---------------------------------------------------------------------------
# 2. Next steps
# ---------------------------------------------------------------------------

STANDARD_ACTIONS = {
    "Contribute": (
        "Share a sighting with a JeevSetu community -- your observation helps BNHS track species.",
        "/explore-communities",
    ),
    "Take a quiz": ("Test what you've learned with a quick quiz on this topic.", "/chatbot"),
    "Advocate": (
        "Become a BNHS member and support conservation research across India.",
        "https://www.bnhs.org/membership-form",
    ),
}


IN_APP_PATHS = {"/explore-communities", "/chatbot", "/publications", "/rewards"}
KNOWN_BNHS_LINKS = {
    "https://www.bnhs.org/membership-form",
    "https://www.bnhs.org/donate",
    "https://www.bnhs.org/nature-trails",
    "https://www.bnhs.org/publication",
    "https://www.bnhs.org/news-letter",
    "https://collections.bnhs.org",
}
DEFAULT_LINKS = {
    "Learn": "https://www.bnhs.org/publication",
    "Explore": "https://www.bnhs.org/nature-trails",
    "Play": "/chatbot",
    "Take a quiz": "/chatbot",
    "Contribute": "/explore-communities",
    "Advocate": "https://www.bnhs.org/membership-form",
}


def _clean_link(link: str | None, label: str, allowed: set[str]) -> str:
    """LLMs happily invent plausible-looking URLs; only keep links known to
    resolve, and repair in-app paths the model glued onto bnhs.org."""
    link = (link or "").strip().rstrip("/")
    for path in IN_APP_PATHS:
        if link == path or link.endswith(path):
            return path
    if link in allowed or link in KNOWN_BNHS_LINKS:
        return link
    return DEFAULT_LINKS.get(label, "https://www.bnhs.org/publication")


def _fallback_next_steps(title: str) -> NextStepsResponse:
    hits = knowledge_base.search(title, limit=2)
    actions = []
    if hits:
        doc = hits[0].document
        actions.append(
            NextStepAction(
                action_label="Learn",
                description=f"Read the BNHS record “{doc.title}” to go deeper on {title}.",
                direct_link=doc.url,
            )
        )
    else:
        actions.append(
            NextStepAction(
                action_label="Learn",
                description="Browse BNHS publications, from Hornbill magazine to the JBNHS archive.",
                direct_link="https://www.bnhs.org/publication",
            )
        )
    actions.append(
        NextStepAction(
            action_label="Explore",
            description="Join a BNHS nature trail and see wildlife in the field with expert naturalists.",
            direct_link="https://www.bnhs.org/nature-trails",
        )
    )
    for label, (description, link) in STANDARD_ACTIONS.items():
        if len(actions) == 4:
            break
        actions.append(
            NextStepAction(action_label=label, description=description, direct_link=link)
        )
    return NextStepsResponse(actions=actions)


def get_next_steps(body: NextStepsQuery) -> NextStepsResponse:
    """Structured, actionable next-step recommendations."""
    resource = body.current_resource
    interests = (
        ", ".join(body.user_interests)
        if body.user_interests
        else "wildlife conservation, learning, volunteering"
    )
    related = [hit.document for hit in knowledge_base.search(resource.title, limit=4)]

    system = (
        "You are an expert conservation strategist for the Bombay Natural History Society (BNHS). "
        "Respond with a JSON object only, matching exactly this shape: "
        '{"actions": [{"action_label": "Learn|Explore|Play|Take a quiz|Contribute|Advocate", '
        '"description": "string", "direct_link": "string or null"}]} -- return exactly 4 actions.'
    )
    prompt = (
        f"A user is interested in this topic/resource:\n"
        f"Title: {resource.title}\n"
        f"Type: {resource.type}\n"
        f"Content: {resource.content}\n\n"
        f"Their stated interests: {interests}.\n\n"
        f"Related BNHS archive records (prefer linking to these):\n{_context_block(related, 200)}\n"
        f"Record links: {[doc.url for doc in related]}\n\n"
        "Recommend 4 actions that turn this passive reader into an active BNHS participant/advocate. "
        "Only use links from the records above or these real BNHS pages: "
        "https://www.bnhs.org/membership-form, https://www.bnhs.org/donate, "
        "https://www.bnhs.org/nature-trails, https://www.bnhs.org/publication, "
        "https://www.bnhs.org/news-letter, https://collections.bnhs.org. "
        "For contributing sightings inside this app use /explore-communities; for quizzes use /chatbot."
    )

    try:
        data = _generate_json(system, prompt)
        response = NextStepsResponse.model_validate(data)
        if response.actions:
            allowed = {doc.url for doc in related if doc.url}
            for action in response.actions:
                action.direct_link = _clean_link(action.direct_link, action.action_label, allowed)
            return response
    except Exception:  # noqa: BLE001 -- LLMUnavailable or a schema mismatch
        pass
    return _fallback_next_steps(resource.title)


# ---------------------------------------------------------------------------
# 3. Quiz
# ---------------------------------------------------------------------------


def _species_facts(doc: Document) -> dict | None:
    match = re.match(r"^(?P<name>.+?) is (?:a|an) .*?species", doc.content)
    title = re.match(r"^(?P<sci>[^()]+?)\s*\((?P<common>[^)]+)\)$", doc.title)
    if not match or not title:
        return None
    facts = {"common": title["common"].strip(), "scientific": title["sci"].strip()}
    for rank in ("family", "order", "class"):
        found = re.search(rf"\b{rank} ([A-Z][a-z]+)", doc.content)
        if found:
            facts[rank] = found.group(1)
    status = re.search(r"IUCN conservation status: ([^.]+)\.", doc.content)
    if status:
        facts["status"] = status.group(1).strip()
    return facts


def _distractors(
    correct: str, pool: list[str], rng: random.Random, count: int = 3
) -> list[str] | None:
    choices = sorted({value for value in pool if value and value != correct})
    if len(choices) < count:
        return None
    return rng.sample(choices, count)


def _question_from_species(
    doc: Document, all_facts: list[dict], rng: random.Random
) -> QuizQuestion | None:
    facts = _species_facts(doc)
    if not facts:
        return None
    same_class = [f for f in all_facts if f.get("class") == facts.get("class")] or all_facts
    templates = []
    if facts.get("status"):
        templates.append(
            (
                f"What is the IUCN conservation status of the {facts['common']} ({facts['scientific']})?",
                facts["status"],
                [f.get("status") for f in all_facts],
                f"The BNHS species record lists the {facts['common']} as {facts['status']}.",
            )
        )
    if facts.get("family"):
        templates.append(
            (
                f"Which family does the {facts['common']} belong to?",
                facts["family"],
                [f.get("family") for f in same_class],
                f"The {facts['common']} ({facts['scientific']}) belongs to the family {facts['family']}"
                + (f", order {facts['order']}." if facts.get("order") else "."),
            )
        )
    templates.append(
        (
            f"What is the scientific name of the {facts['common']}?",
            facts["scientific"],
            [f.get("scientific") for f in same_class],
            f"{facts['scientific']} is the scientific name of the {facts['common']}.",
        )
    )
    rng.shuffle(templates)
    for question, answer, pool, explanation in templates:
        wrong = _distractors(answer, pool, rng)
        if not wrong:
            continue
        options = wrong + [answer]
        rng.shuffle(options)
        return QuizQuestion(
            question=question,
            options=options,
            correct_answer=options.index(answer),
            explanation=explanation,
            source_reference=doc.title,
        )
    return None


@lru_cache
def _all_species_facts() -> tuple[tuple[Document, dict], ...]:
    pairs = []
    for doc in knowledge_base.get_knowledge_base().of_type("species"):
        facts = _species_facts(doc)
        if facts:
            pairs.append((doc, facts))
    return tuple(pairs)


def build_archive_quiz(topic: str, num_questions: int, seed: str | None = None) -> QuizResponse:
    """Multiple-choice questions generated straight from BNHS species records.

    Picks species matching the topic where possible (topped up with
    threatened species so there's always enough material), and draws
    distractors from related species so the options are plausible.
    """
    rng = random.Random(seed if seed is not None else topic.lower())
    pairs = _all_species_facts()
    facts_by_id = {doc.id: facts for doc, facts in pairs}
    all_facts = [facts for _, facts in pairs]

    matched = [
        hit.document
        for hit in knowledge_base.search(topic, limit=40, source_types={"species"})
        if hit.document.id in facts_by_id
    ]
    threatened = [
        doc
        for doc, facts in pairs
        if facts.get("status") in {"Critically Endangered", "Endangered", "Vulnerable"}
    ]
    rng.shuffle(threatened)
    pool = list(dict.fromkeys(matched[: num_questions * 3] + threatened))

    questions: list[QuizQuestion] = []
    used_answers: set[str] = set()
    for doc in pool:
        if len(questions) >= num_questions:
            break
        question = _question_from_species(doc, all_facts, rng)
        if question and question.question not in used_answers:
            used_answers.add(question.question)
            questions.append(question)
    return QuizResponse(questions=questions)


def _valid_llm_quiz(data: dict, num_questions: int) -> QuizResponse | None:
    try:
        quiz = QuizResponse.model_validate(data)
    except Exception:  # noqa: BLE001
        return None
    questions = [
        q
        for q in quiz.questions
        if len(q.options) == 4 and 0 <= q.correct_answer < 4 and len(set(q.options)) == 4
    ]
    return QuizResponse(questions=questions[:num_questions]) if questions else None


def get_quiz(body: QuizQuery) -> QuizResponse:
    """RAG-grounded multiple-choice quiz generation."""
    matches = [hit.document for hit in knowledge_base.search(body.topic, limit=6)]
    if matches:
        context_text = _context_block(matches, 400)
    else:
        context_text = "No specific BNHS documents matched this topic -- use general Indian wildlife conservation knowledge."

    system = (
        "You are an educational quiz designer for BNHS. Respond with a JSON object only, matching exactly: "
        '{"questions": [{"question": "string", "options": ["string", "string", "string", "string"], '
        '"correct_answer": 0, "explanation": "string", "source_reference": "string or null"}]}. '
        "options must contain exactly 4 distinct items; correct_answer is the 0-based index of the correct option."
    )
    prompt = (
        f'Generate a {body.num_questions}-question multiple-choice quiz about "{body.topic}".\n\n'
        "Ground your questions in this retrieved context where possible -- cite the matching title in "
        "source_reference. If the context is insufficient for a question, use only well-established, "
        "widely documented facts about Indian wildlife (no trivia you are unsure of, such as state "
        "symbols) and leave source_reference null. Every correct answer must be unambiguously true.\n\n"
        f"<CONTEXT>\n{context_text}\n</CONTEXT>"
    )

    try:
        quiz = _valid_llm_quiz(_generate_json(system, prompt), body.num_questions)
        if quiz:
            return quiz
    except LLMUnavailable:
        pass
    # Seeded by date so the offline quiz (and so the daily question) varies day to day.
    return build_archive_quiz(
        body.topic, body.num_questions, seed=f"{body.topic.lower()}|{date.today()}"
    )


# ---------------------------------------------------------------------------
# 4. Ask BNHS (chat)
# ---------------------------------------------------------------------------


def _sources(documents: list[Document]) -> list[AskSource]:
    return [
        AskSource(
            title=doc.title, excerpt=doc.summary(220), url=doc.url, content_type=doc.content_type
        )
        for doc in documents
    ]


def _archive_answer(question: str, documents: list[Document]) -> str:
    if not documents:
        return (
            "I couldn't find anything in the BNHS archive about that. Try naming a species "
            "(e.g. “Great Indian Bustard”), a place, or a BNHS publication like Hornbill."
        )
    lines = ["Here's what the BNHS archive has on that:"]
    for doc in documents[:3]:
        lines.append(f"• {doc.title} — {doc.summary(240)}")
    lines.append("Open the sources below for the full records.")
    return "\n".join(lines)


def ask(body: AskRequest) -> AskResponse:
    # Fold the previous user turn into retrieval so follow-ups like
    # "what does it eat?" still find the right species.
    previous = next((turn.content for turn in reversed(body.history) if turn.role == "user"), "")
    documents = [
        hit.document
        for hit in knowledge_base.search(f"{body.question} {previous}".strip(), limit=5)
    ]
    if not documents and previous:
        documents = [hit.document for hit in knowledge_base.search(body.question, limit=5)]

    system = (
        "You are the BNHS Knowledge Assistant for JeevSetu, helping people learn about Indian "
        "wildlife and the Bombay Natural History Society. Answer using the numbered archive records "
        "provided; cite them inline like [1]. If the records don't cover the question, say so briefly "
        "and give careful general knowledge, clearly marked as such. Keep answers under 180 words. "
        'Respond with JSON only: {"answer": "string", "used_sources": [1, 2]}'
    )
    history = "\n".join(f"{turn.role}: {turn.content}" for turn in body.history[-6:])
    prompt = (
        f"Conversation so far:\n{history}\n\n" if history else ""
    ) + f"Question: {body.question}\n\n<RECORDS>\n{_context_block(documents)}\n</RECORDS>"

    try:
        data = _generate_json(system, prompt)
        answer = str(data.get("answer") or "").strip()
        if answer:
            used = [
                documents[index - 1]
                for index in data.get("used_sources") or []
                if isinstance(index, int) and 1 <= index <= len(documents)
            ]
            return AskResponse(
                answer=answer, sources=_sources(used or documents[:3]), generated_by="llm"
            )
    except LLMUnavailable:
        pass

    return AskResponse(
        answer=_archive_answer(body.question, documents),
        sources=_sources(documents[:3]),
        generated_by="archive",
    )
