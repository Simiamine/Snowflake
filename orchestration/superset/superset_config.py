import os

# Secret
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "change-me-please")
ENABLE_TEMPLATE_PROCESSING = True

# 1) Couleurs par libellé (doivent matcher EXACTEMENT les valeurs dans tes séries)
LABEL_COLORS = {
    "negative": "#E74C3C",        # rouge
    "neutral":  "#95A5A6",        # gris
    "positive": "#27AE60",        # vert
    "full moon": " #9B59B6",      # violet
    "not full moon": "#2980B9",   # bleu
}

# 2) Ta palette personnalisée
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "airbnb_theme",
        "label": "Airbnb Theme",
        "colors": ["#27AE60", "#95A5A6", "#E74C3C", "#2980B9", "#9B59B6"],
    }
]

# 3) La définir comme palette par défaut dans l’UI
DEFAULT_CATEGORICAL_COLOR_SCHEME = "airbnb_theme"
