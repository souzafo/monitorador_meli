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
import re

# Carrega variáveis de ambiente
load_dotenv()

# 🔐 Secrets e Variáveis
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
PRODUCT_URLS = os.getenv("PRODUCT_URLS", "").split(",")
SEND_NOTIFICATIONS = os.getenv("SEND_NOTIFICATIONS", "False").lower() == "true"
SEND_STATUS_TELEGRAM = os.getenv("SEND_STATUS_TELEGRAM", "False").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
RODANDO_GITHUB = os.getenv("GITHUB_ACTIONS", "false").lower() == "true"

# Timezone e log
br_tz = pytz.timezone("America/Sao_Paulo")
logging.basicConfig(level=logging.INFO)

# Gera nome de arquivo seguro para armazenar preços
def gerar_nome_arquivo(url):
    slug = re.sub(r'\W+', '_', url)
    return os.path.join("precos", f"menor_preco_{slug[:100]}.json")

# Extrai o preço da página
def extrair_preco(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        reais = soup.find("span", class_="andes-money-amount__fraction").get_text()
        centavos = soup.find("span", class_="andes-money-amount__cents")
        centavos = centavos.get_text() if centavos else "00"
        return float(f"{reais}.{centavos}")
    except Exception as e:
        logging.error(f"❌ Erro ao extrair preço de {url}: {e}")
        return None

# Envia e-mail
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

# Envia mensagem no Telegram
async def enviar_telegram(mensagem):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
        logging.info("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        logging.error(f"❌ Erro ao enviar mensagem no Telegram: {e}")

# Monitora os preços
async def monitorar():
    origem = "GitHub Actions" if RODANDO_GITHUB else "Execução Local"
    br_now = datetime.now(br_tz).strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{br_now}] 🔎 Iniciando monitoramento ({origem})...")

    for url in PRODUCT_URLS:
        preco_atual = extrair_preco(url)
        if preco_atual:
            arquivo_preco = gerar_nome_arquivo(url)
            try:
                with open(arquivo_preco, "r") as file:
                    data = json.load(file)
                    menor_preco = data.get("menor_preco", float("inf"))
            except (FileNotFoundError, json.JSONDecodeError):
                menor_preco = float("inf")

            logging.info(f"💡 Produto: {url}")
            logging.info(f"🔸 Preço atual: R$ {preco_atual:.2f} | Menor registrado: R$ {menor_preco:.2f}")

            if preco_atual < menor_preco or DEBUG_MODE:
                if preco_atual < menor_preco:
                    logging.info(f"💰 Novo menor preço encontrado para {url}!")
                    with open(arquivo_preco, "w") as file:
                        json.dump({"menor_preco": preco_atual}, file)

                mensagem = f"🔔 Notificação ({origem}): {url} - R$ {preco_atual:.2f}".replace('.', ',')
                enviar_email(mensagem)
                await enviar_telegram(mensagem)

            elif SEND_NOTIFICATIONS:
                mensagem = f"ℹ️ Preço atual ({origem}): {url} - R$ {preco_atual:.2f}".replace('.', ',')
                enviar_email(mensagem)
                await enviar_telegram(mensagem)

# Envia status a cada hora
def verificar_status():
    origem = "GitHub Actions" if RODANDO_GITHUB else "Execução Local"
    br_now = datetime.now(br_tz).strftime("%Y-%m-%d %H:%M:%S")
    for url in PRODUCT_URLS:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                msg = f"✅ [{br_now}] Estou vivo ({origem})! Produto acessível: {url}"
                logging.info(msg)
                if SEND_STATUS_TELEGRAM:
                    asyncio.run(enviar_telegram(msg))
            else:
                msg = f"❌ [{br_now}] Produto respondeu com erro {response.status_code} ({origem}): {url}"
                logging.warning(msg)
                if SEND_STATUS_TELEGRAM:
                    asyncio.run(enviar_telegram(msg))
        except Exception as e:
            msg = f"❌ [{br_now}] Erro ao acessar o produto ({origem}): {url} | Erro: {e}"
            logging.error(msg)
            if SEND_STATUS_TELEGRAM:
                asyncio.run(enviar_telegram(msg))

# Agendamentos
if __name__ == "__main__":
    schedule.every().day.at("00:00").do(lambda: asyncio.run(monitorar()))
    schedule.every().day.at("06:00").do(lambda: asyncio.run(monitorar()))
    schedule.every().day.at("12:00").do(lambda: asyncio.run(monitorar()))
    schedule.every().day.at("18:00").do(lambda: asyncio.run(monitorar()))
    schedule.every().hour.at(":00").do(verificar_status)

    while True:
        schedule.run_pending()
        time.sleep(1)
