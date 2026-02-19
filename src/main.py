from datetime import date

from .config import METALS, ALERT_THRESHOLD, GMAIL_USER
from .provider import get_latest_close_usd
from .db import init_db, save_price, get_yesterday_price
from .alerts import check_alert
from .charts import generate_chart
from .emailer import send_daily_report_email, send_email


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

        # 1) Precio de hoy (USD)
        today_price = get_latest_close_usd(ticker)

        # 2) Precio de ayer (último día anterior a hoy)
        yesterday_price = get_yesterday_price(metal_name)

        # 3) Guardar en DB (tu db.py ya evita duplicados con UNIQUE + ON CONFLICT)
        save_price(metal_name, today_price)

        # 4) Calcular % cambio
        change = pct_change(today_price, yesterday_price)

        # 5) Guardar fila para el reporte diario
        report_rows.append({
            "metal": metal_name,
            "ticker": ticker,
            "today": today_price,
            "yesterday": yesterday_price,
            "change_pct": change,
        })

        # 6) Comprobar alerta
        msg = check_alert(metal_name, today_price, yesterday_price, ALERT_THRESHOLD)
        if msg:
            alerts.append(msg)

            # 🚨 Email inmediato SOLO si hay alerta
            send_email(
                to_email=GMAIL_USER,
                subject=f"🚨 Metals Alert: {metal_name}",
                body=msg
            )

        # 7) Generar gráfico y adjuntarlo al reporte diario
        chart_path = generate_chart(metal_name)
        if chart_path:
            chart_paths.append(chart_path)
            print(f"Chart saved: {chart_path}")

    # 8) Email diario con resumen + gráficos
    subject = f"Metals Daily Report (USD) — {date.today().isoformat()}"
    send_daily_report_email(
        to_email=GMAIL_USER,
        subject=subject,
        rows=report_rows,
        alerts=alerts,
        chart_paths=chart_paths,
    )

    print("Done.")


if __name__ == "__main__":
    run()
