from pathlib import Path
import matplotlib.pyplot as plt
from .db import get_prices
from .config import CHARTS_DIR

def generate_chart(metal: str) -> str | None:
    rows = get_prices(metal)
    if not rows:
        return None

    dates = [r[0] for r in rows]
    prices = [r[1] for r in rows]

    out_dir = Path(CHARTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{metal.lower()}.png"

    plt.figure()
    plt.plot(dates, prices, marker="o")
    plt.title(f"{metal} (USD) - Daily Close")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

    return str(out_path)