import os
import sqlite3
from datetime import date
from .config import DB_PATH


def init_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metal TEXT NOT NULL,
            price REAL NOT NULL,
            day TEXT NOT NULL
        )
        """
    )

    # Esto asegura "1 registro por metal y día" incluso si la DB se creó antes sin UNIQUE
    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_prices_metal_day ON prices(metal, day)"
    )

    conn.commit()
    conn.close()


def save_price(metal: str, price: float, day: str | None = None):
    """
    Guarda el precio del metal para un día.
    Si ya existe (metal, day), actualiza el precio (evita duplicados).
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
    Devuelve el precio más reciente anterior al de hoy, si existe.
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
    Devuelve lista (day, price) ordenada asc.
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
