import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from .config import GMAIL_USER, GMAIL_APP_PASSWORD

def _fmt_money(x: float | None) -> str:
    if x is None:
        return "—"
    return f"${x:,.2f}"

def _fmt_pct(x: float | None) -> str:
    if x is None:
        return "—"
    sign = "+" if x >= 0 else ""
    return f"{sign}{x:.2f}%"

def send_email_html(
    to_email: str,
    subject: str,
    html_body: str,
    attachments: list[str] | None = None,
):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    attachments = attachments or []
    for path in attachments:
        if not path:
            continue
        if not os.path.exists(path):
            continue

        with open(path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(path)}"'
        msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())


def send_daily_report_email(
    to_email: str,
    subject: str,
    rows: list[dict],
    alerts: list[str],
    chart_paths: list[str],
):
    # Build HTML table
    table_rows = ""
    for r in rows:
        table_rows += f"""
        <tr>
          <td><b>{r['metal']}</b></td>
          <td>{r['ticker']}</td>
          <td>{_fmt_money(r['today'])}</td>
          <td>{_fmt_money(r['yesterday'])}</td>
          <td>{_fmt_pct(r['change_pct'])}</td>
        </tr>
        """

    alerts_html = ""
    if alerts:
        alerts_html = "<ul>" + "".join([f"<li>{a}</li>" for a in alerts]) + "</ul>"
    else:
        alerts_html = "<p>No alerts triggered today ✅</p>"

    charts_list = ""
    if chart_paths:
        charts_list = "<ul>" + "".join([f"<li>{os.path.basename(p)}</li>" for p in chart_paths]) + "</ul>"
    else:
        charts_list = "<p>No charts available.</p>"

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background:#ffffff; color:#111;">
        <h2 style="margin-bottom: 6px;">{subject}</h2>

        <h3>📌 Summary</h3>
        <table border="1" cellpadding="10" cellspacing="0" style="border-collapse:collapse;">
          <tr style="background:#f2f2f2;">
            <th>Metal</th>
            <th>Ticker</th>
            <th>Today</th>
            <th>Yesterday</th>
            <th>Change</th>
          </tr>
          {table_rows}
        </table>

        <h3 style="margin-top:18px;">🚨 Alerts</h3>
        {alerts_html}

        <h3 style="margin-top:18px;">📈 Charts (attached)</h3>
        {charts_list}

        <hr />
        <p style="color:#666;">Generated automatically by your Metals Alert Bot.</p>
      </body>
    </html>
    """

    send_email_html(
        to_email=to_email,
        subject=subject,
        html_body=html,
        attachments=chart_paths,
    )
