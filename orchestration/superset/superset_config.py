import os

# Secret
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "change-me-please")
ENABLE_TEMPLATE_PROCESSING = True

# 1) Couleurs par libellé (doivent matcher EXACTEMENT les valeurs dans tes séries)
LABEL_COLORS = {
    # Sentiment Analysis
    "negative": "#E74C3C",        # rouge
    "neutral":  "#95A5A6",        # gris
    "positive": "#27AE60",        # vert
    # Full Moon Analysis
    "full moon": " #9B59B6",      # violet
    "not full moon": "#2980B9",   # bleu
    # Room Types Airbnb
    "Entire home/apt": "#E67E22", # orange
    "Hotel room": "#F39C12",      # jaune/orange
    "Private room": "#3498DB",    # bleu clair
    "Shared room": "#1ABC9C",     # turquoise
}

# 2) Ta palette personnalisée
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "airbnb_theme",
        "label": "Airbnb Theme",
        "colors": [
            "#27AE60",  # vert (positive)
            "#95A5A6",  # gris (neutral)  
            "#E74C3C",  # rouge (negative)
            "#2980B9",  # bleu (not full moon)
            "#9B59B6",  # violet (full moon)
            "#E67E22",  # orange (Entire home/apt)
            "#F39C12",  # jaune/orange (Hotel room)
            "#3498DB",  # bleu clair (Private room)
            "#1ABC9C",  # turquoise (Shared room)
        ],
    }
]

# 3) La définir comme palette par défaut dans l’UI
DEFAULT_CATEGORICAL_COLOR_SCHEME = "airbnb_theme"
