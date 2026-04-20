"""CoolNest — shared configuration (copy to config.py and fill in your values)"""

PROJECT_ID    = "your-gcp-project-id"
LIVE_LOCATION = "us-central1"
BQ_LOCATION   = "US"
LIVE_MODEL    = "gemini-live-2.5-flash-native-audio"
BQ_DATASET    = "coolnest"
PORT          = 7778

# ── Demo users (change passwords before any real deployment) ───────────────
USERS = {
    "saurabh": {
        "id": "saurabh",
        "password": "CHANGE_ME",
        "name": "Saurabh Mangal",
        "loyalty_tier": "platinum",
        "email": "user@example.com",
    },
    "rajan": {
        "id": "rajan",
        "password": "CHANGE_ME",
        "name": "Rajan Kumar",
        "loyalty_tier": "gold",
        "email": "user2@example.com",
    },
    "vamsi": {
        "id": "vamsi",
        "password": "CHANGE_ME",
        "name": "Vamsi Reddy",
        "loyalty_tier": "silver",
        "email": "user3@example.com",
    },
    "veena": {
        "id": "veena",
        "password": "CHANGE_ME",
        "name": "Veena Sharma",
        "loyalty_tier": "platinum",
        "email": "user4@example.com",
    },
}

TIER_LABELS = {
    "platinum": "Platinum Member ★★★",
    "gold":     "Gold Member ★★",
    "silver":   "Silver Member ★",
    "bronze":   "Bronze Member",
}

DISCOUNT_LIMITS = {
    "specialist": 0,
    "supervisor": 10,
    "manager":    25,
}
