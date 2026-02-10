import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

def send_email(receiver_email, topic, questions):
    sender_email = os.getenv("GMAIL_EMAIL")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not sender_password:
        print("❌ Gmail credentials not found in .env")
        return

    msg = EmailMessage()
    msg["Subject"] = f"{topic} – AI Generated Questions"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(questions)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Error sending email:", e)
