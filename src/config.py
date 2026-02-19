import os
from dotenv import load_dotenv

load_dotenv()

# Umbral de alerta (%)
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "6"))

# Email (Gmail)
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

# Base de datos / rutas
DB_PATH = "data/metals.sqlite"
CHARTS_DIR = "docs/charts"

# Metales a seguir (ticker Yahoo Finance)
# Oro (futuro): GC=F, Plata: SI=F, Platino: PL=F
METALS = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F",
}
