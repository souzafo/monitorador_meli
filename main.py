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
import pytz

# Carregar variáveis de ambiente
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
URL = os.getenv("PRODUCT_URL")
SEND_NOTIFICATIONS = os.getenv("SEND_NOTIFICATIONS", "False").lower() == "true"
SEND_STATUS_TELEGRAM = os.getenv("SEND_STATUS_TELEGRAM", "False").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Configura fuso horário e logs
br_tz = pytz.timezone("America/Sao_Paulo")
logging.basicConfig(level=logging.INFO)

print("🔧 URL do Produto:", os.getenv("PRODUCT_URL"))

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

def enviar_email(mensagem):
    msg = MIMEText(mensagem)
    msg["Subject"] = "💰 Alerta de Preço!"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        logging.info("✅ E-mail enviado com sucesso!")
    except Exception as e:
        logging.error(f"❌ Erro ao enviar e-mail: {e}")

async def enviar_telegram(mensagem):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
        logging.info("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        logging.error(f"❌ Erro ao enviar mensagem no Telegram: {e}")

async def monitorar():
    br_now = datetime.now(br_tz).strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{br_now}] 🔎 Verificando preço...")

    preco_atual = extrair_preco()
    if preco_atual:
        try:
            with open("menor_preco.json", "r") as file:
                data = json.load(file)
                menor_preco = data.get("menor_preco", float("inf"))
        except (FileNotFoundError, json.JSONDecodeError):
            menor_preco = float("inf")

        logging.info(f"Preço atual: R$ {preco_atual:.2f} | Menor registrado: R$ {menor_preco:.2f}")

        if preco_atual < menor_preco or DEBUG_MODE:
            if preco_atual < menor_preco:
                logging.info("💰 Novo menor preço encontrado!")
                with open("menor_preco.json", "w") as file:
                    json.dump({"menor_preco": preco_atual}, file)

            mensagem = f"🔔 Notificação: R$ {preco_atual:.2f}".replace('.', ',')
            enviar_email(mensagem)
            await enviar_telegram(mensagem)

        elif SEND_NOTIFICATIONS:
            mensagem = f"ℹ️ Preço atual do produto: R$ {preco_atual:.2f}".replace('.', ',')
            enviar_email(mensagem)
            await enviar_telegram(mensagem)

def verificar_status():
    br_now = datetime.now(br_tz).strftime("%Y-%m-%d %H:%M:%S")
    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            msg = f"✅ [{br_now}] Estou vivo! Produto acessível (200)"
            logging.info(msg)
            if SEND_STATUS_TELEGRAM:
                asyncio.run(enviar_telegram(msg))
        else:
            msg = f"❌ [{br_now}] Produto respondeu com status: {response.status_code}"
            logging.warning(msg)
            if SEND_STATUS_TELEGRAM:
                asyncio.run(enviar_telegram(msg))
    except Exception as e:
        msg = f"❌ [{br_now}] Erro ao acessar o produto: {e}"
        logging.error(msg)
        if SEND_STATUS_TELEGRAM:
            asyncio.run(enviar_telegram(msg))

if __name__ == "__main__":
    # Roda imediatamente ao iniciar
    asyncio.run(monitorar())
    verificar_status()

    # Agendar nos horários fixos (horário UTC ajustado para Brasília: 00h, 06h, 12h, 18h)
    horas_execucao = ["00:00", "06:00", "12:00", "18:00"]
    for hora in horas_execucao:
        schedule.every().day.at(hora).do(lambda: asyncio.run(monitorar()))

    # Healthcheck a cada hora cheia
    schedule.every().hour.at(":00").do(verificar_status)

    while True:
        schedule.run_pending()
        print("🌀 Aguardando próximo agendamento...")
        time.sleep(60)
