import os
import asyncio
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot
import smtplib
from email.mime.text import MIMEText
import json
import logging
import schedule
import time
from datetime import datetime
import pytz  # ou zoneinfo se estiver usando Python 3.9+

# Definindo horário de Brasília
br_tz = pytz.timezone("America/Sao_Paulo")
now_br = datetime.now(br_tz).strftime("%Y-%m-%d %H:%M:%S")

print(f"[{now_br}] 🕒 Monitoramento iniciado (Horário de Brasília)")

# Carrega o .env
load_dotenv()

# Carregar variáveis do ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
URL = os.getenv("PRODUCT_URL")

# Configurações de log
logging.basicConfig(level=logging.INFO)

# Função de extrair o preço do produto
def extrair_preco():
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    
    try:
        reais = soup.find("span", class_="andes-money-amount__fraction").get_text()
        centavos = soup.find("span", class_="andes-money-amount__cents")
        centavos = centavos.get_text() if centavos else "00"
        
        preco = float(f"{reais}.{centavos}")
        return preco
    except Exception as e:
        logging.error(f"Erro ao extrair preço: {e}")
        return None

# Função para enviar o e-mail
def enviar_email(mensagem):
    msg = MIMEText(mensagem)
    msg["Subject"] = "💰 Menor preço encontrado!"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        logging.info("✅ E-mail enviado com sucesso!")
    except Exception as e:
        logging.error(f"❌ Erro ao enviar e-mail: {e}")

# Função assíncrona para enviar mensagem no Telegram
async def enviar_telegram(mensagem):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
        logging.info("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        logging.error(f"❌ Erro ao enviar mensagem no Telegram: {e}")

# Função para monitorar o preço
def monitorar():
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Verificando preço...")

    preco_atual = extrair_preco()

    if preco_atual:
        try:
            with open("menor_preco.json", "r") as file:
                data = json.load(file)
                menor_preco = data.get("menor_preco", float("inf"))
        except (FileNotFoundError, json.JSONDecodeError):
            menor_preco = float("inf")

        logging.info(f"Preço atual: R$ {preco_atual} | Menor registrado: R$ {menor_preco}")

        if preco_atual < menor_preco:
            logging.info("💰 Novo menor preço encontrado!")

            # Atualiza o menor preço
            with open("menor_preco.json", "w") as file:
                json.dump({"menor_preco": preco_atual}, file)

            # Envia notificação por e-mail e Telegram
            mensagem = f"O menor preço encontrado foi: R$ {preco_atual}"

            # Envia e-mail
            enviar_email(mensagem)

            # Envia Telegram (assíncrono)
            asyncio.run(enviar_telegram(mensagem))

if __name__ == "__main__":
    # Agendamento para rodar a cada 30 minutos
    schedule.every(30).minutes.do(monitorar)

    while True:
        schedule.run_pending()
        time.sleep(1)
