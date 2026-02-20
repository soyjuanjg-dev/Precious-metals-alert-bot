from datetime import date
from .config import METALS, ALERT_THRESHOLD, GMAIL_USER
from .provider import get_latest_close_usd
from .db import init_db, save_price, get_yesterday_price
from .charts import generate_chart
from .emailer import send_daily_report_email


def pct_change(today: float, yesterday: float | None) -> float | None:
    if yesterday is None or yesterday == 0:
        return None
    return ((today - yesterday) / yesterday) * 100.0


def run():
    print("Starting metals-usd-alerts...")
    init_db()

    report_rows: list[dict] = []
    alerts: list[str] = []
    chart_paths: list[str] = []

    for metal_name, ticker in METALS.items():
        print(f"Fetching {metal_name} ({ticker})...")

        today_price = get_latest_close_usd(ticker)
        yesterday_price = get_yesterday_price(metal_name)

        save_price(metal_name, today_price)

        change = pct_change(today_price, yesterday_price)

        report_rows.append({
            "metal": metal_name,
            "ticker": ticker,
            "today": today_price,
            "yesterday": yesterday_price,
            "change_pct": change,
        })

        # Alerts list (only if exceeds threshold)
        if change is not None and abs(change) >= ALERT_THRESHOLD:
            direction = "📈 UP" if change > 0 else "📉 DOWN"
            alerts.append(
                f"{metal_name}: {direction} {_fmt_pct_for_alert(change)} (threshold: {ALERT_THRESHOLD}%)"
            )

        chart_path = generate_chart(metal_name)
        if chart_path:
            chart_paths.append(chart_path)
            print(f"Chart saved: {chart_path}")

    subject = f"Metals Daily Report (USD) — {date.today().isoformat()}"

    send_daily_report_email(
        to_email=GMAIL_USER,
        subject=subject,
        rows=report_rows,
        alerts=alerts,
        chart_paths=chart_paths,
    )

    print("Done.")


def _fmt_pct_for_alert(x: float) -> str:
    sign = "+" if x >= 0 else ""
    return f"{sign}{x:.2f}%"


if __name__ == "__main__":
    run()
