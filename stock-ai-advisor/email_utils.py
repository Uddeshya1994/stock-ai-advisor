import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def build_stock_email(
    stock_data,
    confidence_score,
    risk_level,
    debt_1y,
    debt_3y,
    app_url,
    stock_code
):
    return f"""
Hello,

Here is your latest Stock Insight summary.

Company Name: {stock_data.get("Company Name")}
Current Price: ₹ {round(stock_data.get("Current Price"), 2)}
1Y Return (%): {stock_data.get("1Y Return (%)")}

PE Ratio: {stock_data.get("PE Ratio")}
Market Cap: ₹ {round(stock_data.get("Market Cap") / 1_00_00_000, 2)} Cr
ROE: {round(stock_data.get("ROE") * 100, 2)} %

Debt to Equity: {stock_data.get("Debt to Equity")}
Debt Change (1Y): {debt_1y} %
Debt Change (3Y): {debt_3y} %

Confidence Score: {confidence_score} / 100
Beginner Risk Level: {risk_level}

View full analysis:
{app_url}?stock={stock_code}

Note: Educational purpose only.

— Stock Insight App
"""


def send_email(sender_email, receiver_email, subject, body):
    sender_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_password:
        raise ValueError("GMAIL_APP_PASSWORD environment variable not set")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
