"""Builds the bundled Knowledge Hub dataset (backend/data/knowledge_base.json.gz)
from the public BNHS collections API (Omeka S), plus a small set of curated
BNHS programme entries.

The original corpus lived only in the team's Supabase project; this script
makes it reproducible and ships the result with the app, so search, quizzes
and the chatbot work without any external database. Idempotent -- re-run it
to refresh the dataset.

Usage:
    cd backend
    python scripts/build_knowledge_base.py
"""

from __future__ import annotations

import gzip
import json
import re
import sys
import time
from pathlib import Path

import httpx

API = "https://collections.bnhs.org/api/items"
PORTAL = "https://collections.bnhs.org/s"
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json.gz"
AUTHOR = "Bombay Natural History Society (BNHS)"

# (item_set_id, source_type, portal site slug). Order matters: an item that
# sits in several sets (e.g. a Hornbill issue is also a "BNHS Publication")
# keeps the first, most specific source_type.
ITEM_SETS = [
    (48827, "field_guide", "field_guides"),
    (48826, "field_guide", "field_guides"),
    (1092, "species", "specimen"),
    (8, "hornbill", "publications"),
    (948, "buceros", "publications"),
    (7, "newsletter", "publications"),
    (1080, "jbnhs", "publications"),
    (12, "publication", "publications"),
    (2136, "collector", "collectors"),
]

# Field-guide properties worth indexing, in display order.
FIELD_GUIDE_FIELDS = [
    ("bnhsfg:scientificName", "Scientific name"),
    ("bnhsfg:localNames", "Local names"),
    ("bnhsfg:sizeRaw", "Size"),
    ("bnhsfg:fieldCharacters", "Field characters"),
    ("bnhsfg:statusDistributionHabitat", "Status, distribution & habitat"),
    ("bnhsfg:generalHabits", "General habits"),
    ("bnhsfg:food", "Food"),
    ("bnhsfg:voiceAndCalls", "Voice & calls"),
    ("bnhsfg:breeding", "Breeding"),
    ("bnhsfg:migration", "Migration"),
]

# Plain-English names for taxonomic classes, so "endangered birds" finds
# records that only say "class Aves".
CLASS_COMMON_NAMES = {
    "Aves": "bird",
    "Mammalia": "mammal",
    "Reptilia": "reptile",
    "Amphibia": "amphibian",
    "Actinopterygii": "fish",
    "Chondrichthyes": "fish",
    "Insecta": "insect",
    "Arachnida": "arachnid",
    "Gastropoda": "snail",
    "Bivalvia": "mollusc",
    "Malacostraca": "crustacean",
    "Anthozoa": "coral",
}

UNINFORMATIVE = {"?", "none recorded.", "no abstract available.", "n/a", "-"}

CURATED = [
    {
        "id": "bnhs-about",
        "title": "About the Bombay Natural History Society (BNHS)",
        "content": (
            "The Bombay Natural History Society, founded on 15 September 1883, is one of the "
            "largest non-governmental organisations in India engaged in conservation and "
            "biodiversity research. Headquartered at Hornbill House in Mumbai, BNHS works on "
            "species and habitat conservation through research, education and public "
            "awareness, and publishes the Journal of the Bombay Natural History Society (JBNHS), "
            "one of the oldest natural history journals in Asia, and the popular magazine Hornbill. "
            "Dr Salim Ali, the 'Birdman of India', was closely associated with the Society for decades."
        ),
        "url": "https://www.bnhs.org/who-we-are",
        "tags": ["about", "history", "organisation"],
    },
    {
        "id": "bnhs-membership",
        "title": "Become a BNHS member",
        "content": (
            "BNHS membership is open to anyone interested in nature. Members receive Hornbill "
            "magazine, can take part in nature trails, camps and field programmes, get access to "
            "the Society's library and collections, and directly support conservation research "
            "across India. Membership options include individual, family, student and life membership."
        ),
        "url": "https://www.bnhs.org/membership-form",
        "tags": ["membership", "join", "support", "volunteer"],
    },
    {
        "id": "bnhs-vulture-programme",
        "title": "Vulture Conservation Breeding Programme",
        "content": (
            "India's Gyps vultures - the White-rumped, Indian (Long-billed) and Slender-billed "
            "vultures - declined by more than 95% from the 1990s, mainly because of the veterinary "
            "painkiller diclofenac in livestock carcasses. BNHS runs conservation breeding centres, "
            "including the Jatayu Conservation Breeding Centre at Pinjore in Haryana and centres in "
            "Assam, West Bengal and Madhya Pradesh, rears vultures in captivity, and works with "
            "governments to create diclofenac-free Vulture Safe Zones before releasing birds back to the wild."
        ),
        "url": "https://www.bnhs.org/vulturereports",
        "tags": ["vulture", "raptor", "diclofenac", "breeding", "endangered", "conservation"],
    },
    {
        "id": "bnhs-bird-migration",
        "title": "Bird migration and ringing studies",
        "content": (
            "BNHS has pioneered bird ringing (banding) in India since the 1920s. Ringing stations, "
            "such as the one at Point Calimere in Tamil Nadu, study the routes, timing and stopover "
            "sites of migratory birds that use the Central Asian Flyway. Data from ringed birds help "
            "identify wetlands that are critical for waders, ducks and other migrants."
        ),
        "url": "https://www.bnhs.org/listing/species-research",
        "tags": ["migration", "ringing", "birds", "wetlands", "flyway"],
    },
    {
        "id": "bnhs-iba",
        "title": "Important Bird and Biodiversity Areas (IBAs) of India",
        "content": (
            "As the BirdLife International partner in India, BNHS identified over 550 Important Bird "
            "and Biodiversity Areas (IBAs) across the country - sites of global significance for the "
            "conservation of bird populations. The Indian Bird Conservation Network (IBCN) connects "
            "individuals and organisations who monitor and protect these sites."
        ),
        "url": "https://www.bnhs.org/listing/conservation-research",
        "tags": ["iba", "birds", "habitat", "network", "birdlife"],
    },
    {
        "id": "bnhs-cec",
        "title": "Conservation Education Centres",
        "content": (
            "BNHS Conservation Education Centres (CEC) in Mumbai, next to Sanjay Gandhi National "
            "Park, and in Delhi run nature walks, workshops, teacher training and school "
            "programmes that introduce students and citizens to biodiversity and conservation."
        ),
        "url": "https://www.bnhs.org/listing/conservation-education",
        "tags": ["education", "students", "nature walk", "workshop", "camps"],
    },
    {
        "id": "bnhs-nature-camps",
        "title": "Nature camps and field trips",
        "content": (
            "BNHS organises nature camps and field trips across India - from Himalayan bird "
            "watching to marine life explorations - led by experienced naturalists. Camps are a "
            "hands-on way for members to learn field identification, natural history and "
            "responsible wildlife watching."
        ),
        "url": "https://www.bnhs.org/nature-trails",
        "tags": ["camps", "travel", "field trip", "bird watching", "volunteer"],
    },
    {
        "id": "bnhs-citizen-science",
        "title": "Citizen science with BNHS",
        "content": (
            "Citizen scientists contribute sightings, photographs and counts that help BNHS monitor "
            "species and habitats. Programmes include bird counts, wetland surveys and community "
            "monitoring. Careful records - date, location, species, numbers and behaviour - make "
            "observations useful for research and conservation planning."
        ),
        "url": "https://www.bnhs.org/listing/conservation-action",
        "tags": ["citizen science", "observations", "monitoring", "volunteer", "survey"],
    },
    {
        "id": "bnhs-hornbill-magazine",
        "title": "Hornbill magazine",
        "content": (
            "Hornbill is the popular natural history magazine of BNHS, published since 1976. It "
            "carries articles, photo essays and field notes on Indian wildlife and conservation for "
            "a general audience, and the archive of past issues is available in the BNHS collections."
        ),
        "url": "https://www.bnhs.org/publication",
        "tags": ["hornbill", "magazine", "publication", "reading"],
    },
    {
        "id": "bnhs-jbnhs",
        "title": "Journal of the Bombay Natural History Society (JBNHS)",
        "content": (
            "Published continuously since 1886, the Journal of the Bombay Natural History Society "
            "is a peer-reviewed journal on the natural history of South Asia - taxonomy, ecology, "
            "behaviour and conservation. Researchers and naturalists can submit papers and "
            "miscellaneous notes on new records and observations."
        ),
        "url": "https://www.bnhs.org/publication",
        "tags": ["journal", "research", "publication", "science", "submit"],
    },
    {
        "id": "bnhs-donate",
        "title": "Support BNHS conservation",
        "content": (
            "Donations to BNHS fund field research, species recovery programmes such as vulture "
            "breeding, habitat protection, and conservation education. Supporters can donate, "
            "sponsor programmes, or volunteer time and skills."
        ),
        "url": "https://www.bnhs.org/donate",
        "tags": ["donate", "support", "fundraising", "volunteer"],
    },
]


def _values(item: dict, key: str) -> list[str]:
    out = []
    for value in item.get(key) or []:
        text = value.get("@value") or value.get("display_title")
        if text:
            out.append(re.sub(r"\s+", " ", str(text)).strip())
    return out


def _first(item: dict, key: str) -> str | None:
    values = _values(item, key)
    return values[0] if values else None


def _informative(text: str | None) -> bool:
    return bool(text) and text.strip().lower() not in UNINFORMATIVE


def _species_doc(item: dict) -> tuple[str, list[str]]:
    common = _first(item, "wo:commonName")
    scientific = _first(item, "wo:scientificName")
    ranks = [
        (label, _first(item, key))
        for label, key in [
            ("family", "wo:family"),
            ("order", "wo:order"),
            ("class", "wo:class"),
            ("phylum", "wo:phylum"),
            ("kingdom", "wo:kingdom"),
        ]
    ]
    status = _first(item, "wo:conservationStatus")
    name = f"{common} ({scientific})" if common and scientific else (common or scientific or "")
    group = CLASS_COMMON_NAMES.get(_first(item, "wo:class") or "")
    kind = f"a {group} species" if group else "a species"
    parts = [f"{name} is {kind} recorded in the BNHS collections."]
    taxonomy = ", ".join(f"{label} {value}" for label, value in ranks if value)
    if taxonomy:
        parts.append(f"Taxonomy: {taxonomy}.")
    if status:
        parts.append(f"IUCN conservation status: {status}.")
    tags = [v for _, v in ranks if v] + ([status] if status else []) + ([group] if group else [])
    return " ".join(parts), tags


def _field_guide_doc(item: dict) -> tuple[str, list[str]]:
    lines = []
    for key, label in FIELD_GUIDE_FIELDS:
        value = _first(item, key)
        if _informative(value):
            lines.append(f"{label}: {value}")
    linked_species = _first(item, "bnhsfg:species")
    if linked_species:
        lines.insert(0, f"Species: {linked_species}")
    return "\n".join(lines), ["birds", "field guide"]


def _generic_doc(item: dict) -> tuple[str, list[str]]:
    parts = []
    for key in ("dcterms:description", "dcterms:abstract", "dcterms:subject", "dcterms:references"):
        for value in _values(item, key):
            if _informative(value) and value not in parts and value != item.get("o:title"):
                parts.append(value)
    return "\n".join(parts), []


def to_document(item: dict, source_type: str, site: str) -> dict:
    if source_type == "species":
        content, tags = _species_doc(item)
    elif source_type == "field_guide":
        content, tags = _field_guide_doc(item)
    else:
        content, tags = _generic_doc(item)

    title = item.get("o:title") or _first(item, "dcterms:title") or "Untitled"
    if not content:
        content = title
    return {
        "id": f"omeka-{item['o:id']}",
        "source_type": source_type,
        "title": title,
        "content": content,
        "url": f"{PORTAL}/{site}/item/{item['o:id']}",
        "author": AUTHOR,
        "date": _first(item, "dcterms:created"),
        "tags": tags,
    }


def fetch_item_set(client: httpx.Client, item_set_id: int) -> list[dict]:
    items, page = [], 1
    while True:
        for attempt in range(4):
            try:
                response = client.get(
                    API, params={"item_set_id": item_set_id, "per_page": 100, "page": page}
                )
                response.raise_for_status()
                break
            except httpx.HTTPError:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
        batch = response.json()
        if not batch:
            return items
        items.extend(batch)
        if len(batch) < 100:
            return items
        page += 1


def main() -> None:
    documents: dict[str, dict] = {}
    with httpx.Client(
        headers={"User-Agent": "jeevsetu-knowledge-hub/1.0"}, timeout=60, follow_redirects=True
    ) as client:
        for item_set_id, source_type, site in ITEM_SETS:
            items = fetch_item_set(client, item_set_id)
            added = 0
            for item in items:
                doc = to_document(item, source_type, site)
                if doc["id"] not in documents:
                    documents[doc["id"]] = doc
                    added += 1
            print(f"item set {item_set_id} ({source_type}): {len(items)} fetched, {added} new")

    for entry in CURATED:
        documents[entry["id"]] = {
            "source_type": "bnhs_programme",
            "author": AUTHOR,
            "date": None,
            **entry,
        }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(list(documents.values()), ensure_ascii=False, separators=(",", ":"))
    with gzip.open(OUTPUT, "wt", encoding="utf-8") as handle:
        handle.write(payload)
    print(f"\nWrote {len(documents)} documents to {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    sys.exit(main())
