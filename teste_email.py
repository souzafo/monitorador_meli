import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

def enviar_email_teste():
    corpo = "Este é um teste de envio de e-mail via Python 🤖📬"
    msg = MIMEText(corpo)
    msg["Subject"] = "🔔 Teste de e-mail com Python"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print("❌ Erro ao enviar e-mail:", e)

if __name__ == "__main__":
    enviar_email_teste()
