from pathlib import Path
import os
from dotenv import load_dotenv

# 1️⃣ Definir BASE_DIR primero
BASE_DIR = Path(__file__).resolve().parents[1]

# 2️⃣ Luego cargar .env usando BASE_DIR
load_dotenv(BASE_DIR / ".env")

# 3️⃣ Paths absolutos
DB_PATH = BASE_DIR / "data" / "metals.sqlite"
CHARTS_DIR = BASE_DIR / "docs" / "charts"

# 4️⃣ Asegurar carpetas
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# 5️⃣ Variables entorno
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "6"))

# 6️⃣ Metales
METALS = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F",
}