import sqlite3
from datetime import date
from pathlib import Path
from .config import DB_PATH

def init_db():
    # Ensure /data exists
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metal TEXT NOT NULL,
        price REAL NOT NULL,
        day TEXT NOT NULL,
        UNIQUE(metal, day)
    )
    """)

    conn.commit()
    conn.close()


def save_price(metal: str, price: float, day: str | None = None):
    """
    Save price for a given day.
    If (metal, day) already exists, update it (prevents duplicates).
    """
    if day is None:
        day = date.today().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO prices (metal, price, day)
        VALUES (?, ?, ?)
        ON CONFLICT(metal, day) DO UPDATE SET
            price = excluded.price
        """,
        (metal, price, day),
    )

    conn.commit()
    conn.close()


def get_yesterday_price(metal: str) -> float | None:
    """
    Return most recent price before today (if available).
    """
    today = date.today().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT price
        FROM prices
        WHERE metal = ? AND day < ?
        ORDER BY day DESC
        LIMIT 1
        """,
        (metal, today),
    )

    row = cur.fetchone()
    conn.close()
    return float(row[0]) if row else None


def get_prices(metal: str):
    """
    Return list of (day, price) ascending by day.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT day, price
        FROM prices
        WHERE metal = ?
        ORDER BY day ASC
        """,
        (metal,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows
