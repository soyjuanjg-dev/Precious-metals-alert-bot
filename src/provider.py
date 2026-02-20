import yfinance as yf


def get_latest_close_usd(ticker: str) -> float:
    """
    Fetch the latest available daily close price for a given Yahoo Finance ticker (USD).
    Robust against yfinance returning multi-index columns or 1-column DataFrames.
    """
    # Fetch last ~10 days to ensure we get at least one valid close
    df = yf.download(
        tickers=ticker,
        period="10d",
        interval="1d",
        auto_adjust=False,
        progress=False,
        group_by="column",
        threads=True,
    )

    if df is None or df.empty:
        raise RuntimeError(f"No data returned from yfinance for ticker: {ticker}")

    # If columns are MultiIndex (common when multiple tickers are requested),
    # flatten them or select the first level properly.
    # Example MultiIndex: ('Close', 'GC=F')
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        # Try to find the 'Close' column in the first level
        if "Close" in df.columns.get_level_values(0):
            close_df = df["Close"]
            # close_df might be a DataFrame (one column per ticker)
            # If only one column, take it; otherwise take the column matching ticker.
            if hasattr(close_df, "columns"):
                if ticker in close_df.columns:
                    close_series = close_df[ticker]
                else:
                    # fallback: take first column
                    close_series = close_df.iloc[:, 0]
            else:
                close_series = close_df
        else:
            # fallback: take first close-like column if present
            raise RuntimeError(f"MultiIndex columns but 'Close' not found for {ticker}: {df.columns}")
    else:
        # Normal case: single-level columns
        if "Close" not in df.columns:
            raise RuntimeError(f"'Close' column not found for {ticker}. Columns: {list(df.columns)}")
        close_series = df["Close"]

        # Sometimes 'Close' may still be a DataFrame (edge cases)
        if hasattr(close_series, "columns"):
            # pick first column
            close_series = close_series.iloc[:, 0]

    # Clean NaNs and take last available value
    close_series = close_series.dropna()
    if close_series.empty:
        raise RuntimeError(f"No valid Close values for {ticker}")

    last_value = close_series.iloc[-1]

    # last_value MUST be scalar; if not, force scalar extraction
    # (in case it's still a Series due to weird shape)
    if hasattr(last_value, "iloc"):
        last_value = last_value.iloc[-1]

    return float(last_value)