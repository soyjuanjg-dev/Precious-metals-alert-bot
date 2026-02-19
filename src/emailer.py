import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from .config import GMAIL_USER, GMAIL_APP_PASSWORD


# =============================
# SIMPLE EMAIL (for alerts)
# =============================
def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())


# =============================
# DAILY REPORT EMAIL
# =============================
def fmt_money(x):
    if x is None:
        return "—"
    return f"${x:,.2f}"


def fmt_pct(x):
    if x is None:
        return "—"
    sign = "+" if x >= 0 else ""
    return f"{sign}{x:.2f}%"


def send_daily_report_email(to_email, subject, rows, alerts, chart_paths):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    # Build HTML table
    table_rows = ""
    for r in rows:
        table_rows += f"""
        <tr>
          <td><b>{r['metal']}</b></td>
          <td>{r.get('ticker','')}</td>
          <td>{fmt_money(r.get('today'))}</td>
          <td>{fmt_money(r.get('yesterday'))}</td>
          <td>{fmt_pct(r.get('change_pct'))}</td>
        </tr>
        """

    alerts_html = "<br>".join(alerts) if alerts else "No alerts triggered today ✅"

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>{subject}</h2>

        <h3>📌 Summary</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
          <tr style="background:#f2f2f2;">
            <th>Metal</th>
            <th>Ticker</th>
            <th>Today</th>
            <th>Yesterday</th>
            <th>Change</th>
          </tr>
          {table_rows}
        </table>

        <h3>🚨 Alerts</h3>
        <p>{alerts_html}</p>

        <hr>
        <p style="color:#777;">Generated automatically by your Metals Alert Bot.</p>
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    # Attach charts
    for path in chart_paths:
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(path)}"'
            )
            msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
