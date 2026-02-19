import yfinance as yf

def get_latest_close_usd(ticker: str) -> float:
    """
    Devuelve el último 'Close' diario disponible (USD) para el ticker.
    """
    data = yf.download(ticker, period="7d", interval="1d", progress=False)
    if data is None or data.empty:
        raise RuntimeError(f"No data returned for ticker {ticker}")

    # último close disponible
    last_close = data["Close"].dropna().iloc[-1]
    last_close = float(last_close.iloc[0]) if hasattr(last_close, "iloc") else float(last_close)

    return last_close
