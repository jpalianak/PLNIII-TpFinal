from langchain_core.tools import tool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

@tool
def notify_email(input_str: str) -> str:
    """
    Envía un email. La entrada debe tener el formato:
    'destinatario|mensaje'. Si no se especifica destinatario, se usa DEFAULT_RECIPIENT.
    """
    try:
        recipient, message = input_str.split("|", 1)
        recipient = recipient.strip()

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = recipient
        msg["Subject"] = "Notificación del agente AIGE"
        msg.attach(MIMEText(message, "plain"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        return f"Email enviado a {recipient}"
    
    except Exception as e:
        return f"Error al enviar email: {e}"