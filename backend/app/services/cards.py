"""Collectable species cards, bought with coins earned around the app."""

from fastapi import HTTPException, status

from app.services import rewards

RARITY_PRICES = {"Common": 40, "Rare": 80, "Epic": 150, "Legendary": 250}
RARITY_COLORS = {"Common": "#4CAF50", "Rare": "#2196F3", "Epic": "#9C27B0", "Legendary": "#E09B00"}

_CATALOG = [
    {
        "id": "monkey",
        "name": "Jungle Monkey",
        "scientific_name": "Order Primates",
        "rarity": "Common",
        "image": "/cards/monkey.jpg",
        "icon": "paw-print",
        "habitat": "Dense tropical rainforests and canopies.",
        "description": "Agile and highly intelligent, these primates are known for their strong social bonds, curiosity, and incredible swinging abilities.",
        "iucn_status": None,
    },
    {
        "id": "giant-squirrel",
        "name": "Indian Giant Squirrel",
        "scientific_name": "Ratufa indica",
        "rarity": "Common",
        "image": None,
        "icon": "squirrel",
        "habitat": "Deciduous and evergreen forests of peninsular India.",
        "description": "A strikingly coloured, metre-long tree squirrel that leaps up to six metres between branches and rarely comes to the ground.",
        "iucn_status": "Least Concern",
    },
    {
        "id": "blackbuck",
        "name": "Blackbuck",
        "scientific_name": "Antilope cervicapra",
        "rarity": "Common",
        "image": None,
        "icon": "paw-print",
        "habitat": "Open grasslands and scrub of India and Nepal.",
        "description": "One of the fastest antelopes on Earth; adult males have dark coats and long spiralling horns.",
        "iucn_status": "Least Concern",
    },
    {
        "id": "beetle",
        "name": "Rhino Beetle",
        "scientific_name": "Subfamily Dynastinae",
        "rarity": "Rare",
        "image": "/cards/beetle.jpg",
        "icon": "bug",
        "habitat": "Tropical rainforests and woodlands across the globe.",
        "description": "Known for their immense strength and large horns, rhinoceros beetles are among the largest of beetles and can lift incredibly heavy objects.",
        "iucn_status": None,
    },
    {
        "id": "olive-ridley",
        "name": "Olive Ridley Turtle",
        "scientific_name": "Lepidochelys olivacea",
        "rarity": "Rare",
        "image": None,
        "icon": "turtle",
        "habitat": "Warm oceans; nests on beaches such as Gahirmatha, Odisha.",
        "description": "Famous for the arribada -- synchronised mass nesting when thousands of females come ashore together to lay eggs.",
        "iucn_status": "Vulnerable",
    },
    {
        "id": "sarus-crane",
        "name": "Sarus Crane",
        "scientific_name": "Grus antigone",
        "rarity": "Rare",
        "image": None,
        "icon": "bird",
        "habitat": "Wetlands and farmland of northern and central India.",
        "description": "The world's tallest flying bird. Pairs bond for life and perform elaborate trumpeting duets.",
        "iucn_status": "Vulnerable",
    },
    {
        "id": "indian-pangolin",
        "name": "Indian Pangolin",
        "scientific_name": "Manis crassicaudata",
        "rarity": "Rare",
        "image": None,
        "icon": "shield",
        "habitat": "Forests, grasslands and scrub across the Indian subcontinent.",
        "description": "A scaly anteater that rolls into an armoured ball when threatened; heavily trafficked for its scales.",
        "iucn_status": "Endangered",
    },
    {
        "id": "peacock",
        "name": "Peacock",
        "scientific_name": "Pavo cristatus",
        "rarity": "Epic",
        "image": "/cards/peacock.jpg",
        "icon": "feather",
        "habitat": "Forests, agricultural lands, and urban areas in South Asia.",
        "description": "The Indian peafowl, known for its magnificent tail feathers, is a large and brightly colored bird native to the Indian subcontinent.",
        "iucn_status": "Least Concern",
    },
    {
        "id": "great-hornbill",
        "name": "Great Hornbill",
        "scientific_name": "Buceros bicornis",
        "rarity": "Epic",
        "image": None,
        "icon": "bird",
        "habitat": "Evergreen forests of the Western Ghats and North-east India.",
        "description": "A huge fruit-eating bird with a yellow casque. The female seals herself into a tree hollow to nest while the male brings food.",
        "iucn_status": "Vulnerable",
    },
    {
        "id": "indian-vulture",
        "name": "Indian Vulture",
        "scientific_name": "Gyps indicus",
        "rarity": "Epic",
        "image": None,
        "icon": "bird",
        "habitat": "Cliffs and open country across peninsular India.",
        "description": "Populations crashed by over 95% due to the drug diclofenac; BNHS breeding centres are bringing it back.",
        "iucn_status": "Critically Endangered",
    },
    {
        "id": "river-dolphin",
        "name": "Ganges River Dolphin",
        "scientific_name": "Platanista gangetica",
        "rarity": "Epic",
        "image": None,
        "icon": "waves",
        "habitat": "Ganga and Brahmaputra river systems.",
        "description": "India's national aquatic animal. Nearly blind, it navigates muddy rivers by echolocation.",
        "iucn_status": "Endangered",
    },
    {
        "id": "asian-elephant",
        "name": "Asian Elephant",
        "scientific_name": "Elephas maximus",
        "rarity": "Epic",
        "image": None,
        "icon": "paw-print",
        "habitat": "Forests and grasslands from the Western Ghats to the Himalayan foothills.",
        "description": "A keystone species that shapes forests as it moves; India is home to the majority of the world's wild Asian elephants.",
        "iucn_status": "Endangered",
    },
    {
        "id": "bengal-tiger",
        "name": "Bengal Tiger",
        "scientific_name": "Panthera tigris tigris",
        "rarity": "Legendary",
        "image": None,
        "icon": "cat",
        "habitat": "Tropical forests, mangroves and grasslands of India.",
        "description": "India's national animal and the face of Project Tiger; no two tigers share the same stripe pattern.",
        "iucn_status": "Endangered",
    },
    {
        "id": "great-indian-bustard",
        "name": "Great Indian Bustard",
        "scientific_name": "Ardeotis nigriceps",
        "rarity": "Legendary",
        "image": None,
        "icon": "bird",
        "habitat": "Dry grasslands of Rajasthan and Gujarat.",
        "description": "One of the heaviest flying birds, now among the rarest; power-line collisions are a major threat to the last few wild birds.",
        "iucn_status": "Critically Endangered",
    },
]

CATALOG = [
    {**card, "price": RARITY_PRICES[card["rarity"]], "color": RARITY_COLORS[card["rarity"]]}
    for card in _CATALOG
]
CATALOG_BY_ID = {card["id"]: card for card in CATALOG}


def _owned_ids(supabase, user_id: str) -> set[str]:
    rows = supabase.table("user_cards").select("card_id").eq("user_id", user_id).execute().data
    return {row["card_id"] for row in rows}


def _balance(supabase, user_id: str) -> int:
    profile = supabase.table("users").select("coin_balance").eq("id", user_id).limit(1).execute()
    return (profile.data[0].get("coin_balance") or 0) if profile.data else 0


def list_cards(supabase, user_id: str) -> dict:
    owned = _owned_ids(supabase, user_id)
    return {
        "coin_balance": _balance(supabase, user_id),
        "cards": [{**card, "owned": card["id"] in owned} for card in CATALOG],
    }


def collect_card(supabase, user_id: str, card_id: str) -> dict:
    card = CATALOG_BY_ID.get(card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    if card_id in _owned_ids(supabase, user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="You already have this card"
        )
    balance = _balance(supabase, user_id)
    if balance < card["price"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You need {card['price'] - balance} more coins to collect {card['name']}",
        )

    try:
        # (user_id, card_id) is the primary key, so a double-click can't buy twice.
        supabase.table("user_cards").insert({"user_id": user_id, "card_id": card_id}).execute()
    except Exception as exc:  # noqa: BLE001 -- unique violation from either backend
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="You already have this card"
        ) from exc
    rewards.award_coins(supabase, user_id, -card["price"], "card_collected")
    return list_cards(supabase, user_id)
