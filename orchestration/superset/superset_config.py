import os

# Secret
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "change-me-please")
ENABLE_TEMPLATE_PROCESSING = True

# 1) Couleurs par libellé (doivent matcher EXACTEMENT les valeurs dans tes séries)
LABEL_COLORS = {
    # Sentiment Analysis
    "negative": "#E74C3C",        # rouge vif
    "neutral":  "#95A5A6",        # gris neutre
    "positive": "#27AE60",        # vert (positif)
    
    # Full Moon Analysis
    "full moon": "#9B59B6",       # violet (mystique)
    "not full moon": "#2980B9",   # bleu (clair de lune)
    
    # Room Types Airbnb (palette identitaire + contraste)
    "Entire home/apt": "#FF385C",  # rouge Airbnb (Rausch)
    "Hotel room":      "#FC642D",  # orange “hospitality”
    "Private room":    "#00A699",  # teal (Babu)
    "Shared room":     "#00D1C1",  # aqua (contrasté)
}

# 2) Palette personnalisée Airbnb
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "airbnb_theme",
        "label": "Airbnb Theme",
        "colors": [
            "#FF385C",  # Airbnb Red / Entire home/apt
            "#FC642D",  # Hospitality Orange / Hotel room
            "#00A699",  # Teal / Private room
            "#00D1C1",  # Aqua / Shared room
            "#27AE60",  # Vert / Positive
            "#95A5A6",  # Gris / Neutral
            "#E74C3C",  # Rouge vif / Negative
            "#2980B9",  # Bleu / Not full moon
            "#9B59B6",  # Violet / Full moon
        ],
    }
]

# 3) Définir la palette comme défaut dans l’UI
DEFAULT_CATEGORICAL_COLOR_SCHEME = "airbnb_theme"
