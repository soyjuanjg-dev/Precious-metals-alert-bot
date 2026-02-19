import os
import matplotlib.pyplot as plt
from .config import CHARTS_DIR
from .db import get_prices

def generate_chart(metal: str):
    os.makedirs(CHARTS_DIR, exist_ok=True)

    rows = get_prices(metal)
    if len(rows) < 2:
        return None

    days = [r[0] for r in rows]
    prices = [r[1] for r in rows]

    plt.figure()
    plt.plot(days, prices)
    plt.title(f"{metal} (USD) - Daily Close")
    plt.xticks(rotation=45)
    plt.tight_layout()

    filepath = os.path.join(CHARTS_DIR, f"{metal.lower().replace(' ', '_')}.png")
    plt.savefig(filepath)
    plt.close()
    return filepath
