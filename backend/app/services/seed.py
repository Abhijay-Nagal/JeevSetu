"""Demo content for a fresh local install.

Seeds a handful of community members, communities, posts, comments and likes
-- all created through the normal services, so coin balances, like counts and
memberships are consistent -- plus one demo login. Runs only when the local
store has no users yet; set SEED_DEMO_DATA=false to start empty.

Every seeded account can be signed into with just its username; the demo
account is DEMO_USERNAME.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.models.schema import CommunityCreate, ObservationCreate
from app.services import comments, communities, likes, observations, rewards

logger = logging.getLogger(__name__)

PERSONAS = [
    ("meera.kulkarni", "Meera Kulkarni"),
    ("arjun_nair", "Arjun Nair"),
    ("priya.sen", "Priya Sen"),
    ("rohan_deshpande", "Rohan Deshpande"),
    ("ananya.iyer", "Ananya Iyer"),
    ("kabir_singh", "Kabir Singh"),
]

COMMUNITIES = [
    (
        "meera.kulkarni",
        "Western Ghats Birders",
        "Sightings, calls and nesting notes from the forests of the Sahyadris -- hornbills, "
        "flycatchers, endemics and everything in between.",
    ),
    (
        "arjun_nair",
        "Mumbai Urban Wildlife",
        "Leopards of Aarey, flamingos of Sewri, owls in housing societies: wildlife that shares "
        "the city with us.",
    ),
    (
        "priya.sen",
        "Vulture Watch India",
        "Tracking India's recovering vultures. Report roosts, nests and carcass dumps to help "
        "BNHS map safe zones.",
    ),
    (
        "rohan_deshpande",
        "Wetland Watchers",
        "Waders, ducks and migrants at lakes, creeks and mudflats. Winter counts and ringed-bird reports welcome.",
    ),
    (
        "ananya.iyer",
        "Butterflies & Moths of India",
        "From Southern Birdwing to Common Crow -- share host plants, mud-puddling sites and ID questions.",
    ),
    (
        "kabir_singh",
        "Herps of the Deccan",
        "Snakes, lizards and frogs of the Deccan plateau. Safe observation only -- never handle wild snakes.",
    ),
]

MEMBERSHIPS = {
    "Western Ghats Birders": ["arjun_nair", "priya.sen", "ananya.iyer", "rohan_deshpande"],
    "Mumbai Urban Wildlife": ["meera.kulkarni", "kabir_singh", "ananya.iyer"],
    "Vulture Watch India": ["meera.kulkarni", "rohan_deshpande"],
    "Wetland Watchers": ["priya.sen", "arjun_nair", "meera.kulkarni"],
    "Butterflies & Moths of India": ["meera.kulkarni", "kabir_singh"],
    "Herps of the Deccan": ["arjun_nair", "rohan_deshpande", "priya.sen"],
}

# (author, community or None for a global post, species, location, description, days ago)
POSTS = [
    (
        "meera.kulkarni",
        "Western Ghats Birders",
        "Malabar Pied Hornbill",
        "Dandeli, Karnataka",
        "A pair feeding on wild figs right next to the road at 7 am. The male's casque was clearly visible -- "
        "they moved off towards the river after about ten minutes.",
        13,
    ),
    (
        "arjun_nair",
        "Mumbai Urban Wildlife",
        "Indian Leopard",
        "Aarey Colony, Mumbai",
        "Pugmarks on the muddy trail behind Unit 16 this morning, heading towards the forest patch. "
        "Residents say a leopard has been seen near the dairy twice this week.",
        12,
    ),
    (
        "priya.sen",
        "Vulture Watch India",
        "White-rumped Vulture",
        "Pinjore, Haryana",
        "Counted 14 white-rumped vultures soaring over the hills near the breeding centre. "
        "Great to see so many in the wild sky!",
        12,
    ),
    (
        "rohan_deshpande",
        "Wetland Watchers",
        "Greater Flamingo",
        "Sewri Mudflats, Mumbai",
        "Low tide, roughly 2,000 flamingos -- mostly Lesser with a few hundred Greater. "
        "Also spotted a Eurasian Curlew and several Black-tailed Godwits.",
        11,
    ),
    (
        "ananya.iyer",
        "Butterflies & Moths of India",
        "Southern Birdwing",
        "Amboli, Maharashtra",
        "India's largest butterfly nectaring on Lantana at the edge of the forest. Wingspan easily 17-18 cm.",
        10,
    ),
    (
        "kabir_singh",
        "Herps of the Deccan",
        "Indian Rock Python",
        "Bhimashankar, Maharashtra",
        "A large python basking on a rock near the stream, at least 2.5 m. Observed from a distance; "
        "it slid into the undergrowth after a few minutes.",
        10,
    ),
    (
        "meera.kulkarni",
        None,
        "Asian Paradise Flycatcher",
        "Sanjay Gandhi National Park, Mumbai",
        "A white-morph male with its long ribbon tail near the Kanheri caves trail. One of the most beautiful birds I've seen!",
        9,
    ),
    (
        "priya.sen",
        "Wetland Watchers",
        "Bar-headed Goose",
        "Thol Lake, Gujarat",
        "A flock of around 60 bar-headed geese grazing at the lake edge. These birds fly over the Himalaya on migration!",
        9,
    ),
    (
        "arjun_nair",
        "Western Ghats Birders",
        "Malabar Whistling Thrush",
        "Matheran, Maharashtra",
        "Heard the 'whistling schoolboy' before seeing it -- that unmistakable rambling whistle at dawn near a waterfall.",
        8,
    ),
    (
        "rohan_deshpande",
        "Vulture Watch India",
        "Egyptian Vulture",
        "Pune outskirts, Maharashtra",
        "Two adults and a juvenile at the municipal dump near Uruli Devachi. Worth monitoring -- possible nest on the nearby cliff.",
        8,
    ),
    (
        "ananya.iyer",
        "Mumbai Urban Wildlife",
        "Spotted Owlet",
        "Bandra, Mumbai",
        "A pair of spotted owlets roosting in the old banyan tree in our society compound. They call every evening at dusk.",
        7,
    ),
    (
        "kabir_singh",
        "Butterflies & Moths of India",
        "Atlas Moth",
        "Goa, Western Ghats",
        "An Atlas moth resting on a wall near a street light after heavy rain. Huge -- wingspan around 25 cm.",
        7,
    ),
    (
        "meera.kulkarni",
        "Wetland Watchers",
        "Sarus Crane",
        "Bharatpur, Rajasthan",
        "Pair of Sarus cranes performing their courtship dance in the shallow marsh -- loud trumpeting duet!",
        6,
    ),
    (
        "priya.sen",
        None,
        "Indian Grey Hornbill",
        "Lodhi Garden, Delhi",
        "A pair nesting in a hole in a neem tree. The female has sealed herself in; the male is bringing figs every half hour.",
        6,
    ),
    (
        "arjun_nair",
        "Herps of the Deccan",
        "Fan-throated Lizard",
        "Saswad, Pune",
        "Males displaying their bright blue-red dewlaps on the rocky plateau. Breeding season is in full swing.",
        5,
    ),
    (
        "rohan_deshpande",
        "Western Ghats Birders",
        "Great Hornbill",
        "Anshi National Park, Karnataka",
        "Heard the whooshing wingbeats before seeing it -- a single Great Hornbill flying over the valley. Spectacular.",
        5,
    ),
    (
        "ananya.iyer",
        "Butterflies & Moths of India",
        "Blue Mormon",
        "Sanjay Gandhi National Park, Mumbai",
        "Maharashtra's state butterfly visiting Ixora flowers along the trail. Several individuals this morning.",
        4,
    ),
    (
        "kabir_singh",
        "Mumbai Urban Wildlife",
        "Indian Flying Fox",
        "Byculla Zoo grounds, Mumbai",
        "A large colony of flying foxes roosting in the tall trees; counted roughly 300. They leave at dusk to feed.",
        4,
    ),
    (
        "meera.kulkarni",
        "Vulture Watch India",
        "Long-billed Vulture",
        "Ramnagara, Karnataka",
        "Three Long-billed (Indian) Vultures on the cliffs at Ramadevarabetta Vulture Sanctuary. So encouraging!",
        3,
    ),
    (
        "priya.sen",
        "Herps of the Deccan",
        "Malabar Gliding Frog",
        "Amboli, Maharashtra",
        "Several gliding frogs and their foam nests hanging over a forest pool after the first monsoon showers.",
        3,
    ),
    (
        "arjun_nair",
        None,
        "Indian Peafowl",
        "Mayureshwar Wildlife Sanctuary, Maharashtra",
        "Dozens of peafowl in the scrubland, males displaying their full trains. Also spotted a Chinkara herd.",
        2,
    ),
    (
        "rohan_deshpande",
        "Wetland Watchers",
        "Black-headed Ibis",
        "Bhigwan, Maharashtra",
        "Large mixed flock of Black-headed Ibis, Painted Storks and Spoonbills at Ujani backwaters.",
        2,
    ),
    (
        "ananya.iyer",
        "Western Ghats Birders",
        "Nilgiri Flycatcher",
        "Ooty, Tamil Nadu",
        "A Nilgiri Flycatcher in the shola forest near Avalanche -- that deep blue is stunning in the morning light.",
        1,
    ),
    (
        "kabir_singh",
        "Butterflies & Moths of India",
        "Common Crow",
        "Pune",
        "Mud-puddling Common Crows by the dozen near the riverbank. Interesting to see them alongside Blue Tigers.",
        1,
    ),
]

COMMENTS = [
    (
        0,
        "arjun_nair",
        "Wonderful! Were they near the Kali river bridge? I saw a pair there last winter.",
    ),
    (0, "priya.sen", "Fig season is the best time for hornbills. Great record."),
    (
        1,
        "kabir_singh",
        "Stay safe on that trail in the evenings. The forest department has put up camera traps there.",
    ),
    (2, "rohan_deshpande", "That's an encouraging count. Was this near the Jatayu centre?"),
    (3, "meera.kulkarni", "Sewri never disappoints! Did you see any ringed birds?"),
    (3, "ananya.iyer", "Adding this to our winter count sheet, thanks."),
    (4, "kabir_singh", "Lovely! Amboli is the best spot for birdwings in October."),
    (
        5,
        "arjun_nair",
        "Good call keeping your distance. Rock pythons are protected under Schedule I.",
    ),
    (9, "priya.sen", "Please do report the cliff -- Egyptian vulture nests are rare around Pune."),
    (12, "rohan_deshpande", "The duet is one of the best sounds in Indian birding."),
    (13, "meera.kulkarni", "Delhi's hornbills are such a success story."),
    (15, "ananya.iyer", "Anshi is magical. Did you hear the Malabar Trogon too?"),
    (
        18,
        "priya.sen",
        "Ramadevarabetta is so important for the Long-billed Vulture. Thanks for sharing!",
    ),
    (19, "kabir_singh", "Foam nests -- the monsoon has truly arrived."),
    (22, "rohan_deshpande", "Shola birding is the best. Any Nilgiri Laughingthrush?"),
]

# post index -> usernames who liked it
LIKES = {
    0: ["arjun_nair", "priya.sen", "rohan_deshpande", "ananya.iyer"],
    1: ["meera.kulkarni", "kabir_singh", "ananya.iyer"],
    2: ["meera.kulkarni", "rohan_deshpande"],
    3: ["meera.kulkarni", "priya.sen", "arjun_nair", "ananya.iyer", "kabir_singh"],
    4: ["meera.kulkarni", "kabir_singh"],
    5: ["arjun_nair", "rohan_deshpande"],
    6: ["arjun_nair", "priya.sen", "kabir_singh"],
    7: ["meera.kulkarni", "rohan_deshpande"],
    9: ["priya.sen", "meera.kulkarni"],
    12: ["priya.sen", "arjun_nair", "rohan_deshpande", "ananya.iyer"],
    13: ["meera.kulkarni", "arjun_nair"],
    15: ["meera.kulkarni", "ananya.iyer", "arjun_nair"],
    16: ["meera.kulkarni", "kabir_singh"],
    18: ["priya.sen", "rohan_deshpande", "ananya.iyer"],
    19: ["kabir_singh", "arjun_nair"],
    20: ["meera.kulkarni", "priya.sen"],
    22: ["meera.kulkarni", "rohan_deshpande", "arjun_nair"],
}


def _iso(days_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def _create_user(supabase, username: str, name: str, days_ago: float) -> str:
    row = (
        supabase.table("users")
        .insert(
            {
                "username": username,
                "name": name,
                "email": None,
                "role": "contributor",
                "coin_balance": 0,
                "created_at": _iso(days_ago),
            }
        )
        .execute()
        .data[0]
    )
    rewards.award_coins(supabase, row["id"], rewards.COINS_WELCOME_BONUS, "welcome_bonus")
    return row["id"]


def _backdate(supabase, table: str, row_id: str, days_ago: float, *columns: str) -> None:
    stamp = _iso(days_ago)
    supabase.table(table).update({column: stamp for column in columns}).eq("id", row_id).execute()


def seed_demo_content(supabase, demo_username: str) -> None:
    users = {
        username: _create_user(supabase, username, name, 20) for username, name in PERSONAS
    }

    slugs = {}
    for index, (creator, name, description) in enumerate(COMMUNITIES):
        community = communities.create_community(
            supabase, users[creator], CommunityCreate(name=name, description=description)
        )
        _backdate(supabase, "communities", community["id"], 18 - index, "created_at")
        slugs[name] = community["slug"]
        for member in MEMBERSHIPS.get(name, []):
            communities.join_community(supabase, community["id"], users[member])

    post_ids = []
    for author, community_name, species, location, description, days_ago in POSTS:
        post = observations.create_observation(
            supabase,
            users[author],
            ObservationCreate(
                species=species,
                location=location,
                description=description,
                community_slug=slugs[community_name] if community_name else None,
            ),
        )
        _backdate(supabase, "observations", post["id"], days_ago + 0.3, "created_at", "updated_at")
        post_ids.append((post["id"], days_ago))

    for post_index, username, content in COMMENTS:
        post_id, days_ago = post_ids[post_index]
        comment = comments.create_comment(supabase, post_id, users[username], content)
        _backdate(
            supabase, "observation_comments", comment["id"], max(days_ago - 0.2, 0.05), "created_at"
        )

    for post_index, usernames in LIKES.items():
        post_id, _ = post_ids[post_index]
        for username in usernames:
            likes.like_observation(supabase, post_id, users[username])

    # The demo account: a member of a couple of communities with a post of
    # its own, so every screen has something to show on first login.
    demo_id = _create_user(supabase, demo_username, "Demo Explorer", 3)
    for name in ("Western Ghats Birders", "Wetland Watchers"):
        community = communities.get_community_by_slug(supabase, slugs[name])
        communities.join_community(supabase, community["id"], demo_id)
    post = observations.create_observation(
        supabase,
        demo_id,
        ObservationCreate(
            species="Common Kingfisher",
            location="Powai Lake, Mumbai",
            description="A Common Kingfisher diving repeatedly from an overhanging branch -- caught two small fish in five minutes.",
            community_slug=slugs["Wetland Watchers"],
        ),
    )
    _backdate(supabase, "observations", post["id"], 1.5, "created_at", "updated_at")
    for username in ("meera.kulkarni", "rohan_deshpande"):
        likes.like_observation(supabase, post["id"], users[username])
    comment = comments.create_comment(
        supabase, post["id"], users["priya.sen"], "Great sighting! Powai is a kingfisher hotspot."
    )
    _backdate(supabase, "observation_comments", comment["id"], 1.0, "created_at")


def seed_if_empty(supabase, settings) -> bool:
    """Seeds demo content when the store has no users. Returns True if it did."""
    if not settings.seed_demo_data:
        return False
    if supabase.table("users").select("id").limit(1).execute().data:
        return False
    logger.info(
        "Empty data store -- seeding demo communities and the '%s' account", settings.demo_username
    )
    seed_demo_content(supabase, settings.demo_username)
    return True
