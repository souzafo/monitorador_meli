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

# Carrega o .env
load_dotenv()

# Carregar variáveis do ambiente
SEND_NOTIFICATIONS = os.getenv("SEND_NOTIFICATIONS", "True") == "True"  # Se True, enviará as notificações
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"  # Se True, não envia notificações reais
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
URL = os.getenv("PRODUCT_URL")

# Definindo horário de Brasília
br_tz = pytz.timezone("America/Sao_Paulo")
now_br = datetime.now(br_tz).strftime("%Y-%m-%d %H:%M:%S")

# Configurações de log
logging.basicConfig(level=logging.INFO)

# Função de extrair o preço do produto
def extrair_preco():
    logging.info("Iniciando a requisição para verificar o preço...")
    try:
        response = requests.get(URL, timeout=10)  # Timeout de 10 segundos
        response.raise_for_status()  # Levanta erro para status não OK (200)
        soup = BeautifulSoup(response.content, "html.parser")
        
        reais = soup.find("span", class_="andes-money-amount__fraction").get_text()
        centavos = soup.find("span", class_="andes-money-amount__cents")
        centavos = centavos.get_text() if centavos else "00"
        
        preco = float(f"{reais}.{centavos}")
        logging.info(f"Preço extraído: R$ {preco}")
        return preco
    except Exception as e:
        logging.error(f"Erro ao extrair preço: {e}")
        return None

# Função para enviar o e-mail
def enviar_email(mensagem):
    if DEBUG_MODE:
        logging.info(f"DEBUG: E-mail não enviado. Mensagem: {mensagem}")
    else:
        msg = MIMEText(mensagem)
        msg["Subject"] = "💰 Verificação de preço"
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
    if DEBUG_MODE:
        logging.info(f"DEBUG: Mensagem no Telegram não enviada. Mensagem: {mensagem}")
    else:
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
            logging.info("✅ Mensagem enviada no Telegram!")
        except Exception as e:
            logging.error(f"❌ Erro ao enviar mensagem no Telegram: {e}")

# Função para monitorar o preço
async def monitorar():
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

        # Se o preço atual for menor que o registrado, atualiza o menor preço
        if preco_atual < menor_preco:
            logging.info("💰 Novo menor preço encontrado!")

            # Atualiza o menor preço no arquivo
            with open("menor_preco.json", "w") as file:
                json.dump({"menor_preco": preco_atual}, file)

            if SEND_NOTIFICATIONS:
                # Se SEND_NOTIFICATIONS for True, envia a notificação
                mensagem = f"O menor preço encontrado foi: R$ {preco_atual}"

                # Envia e-mail
                enviar_email(mensagem)

                # Envia Telegram (assíncrono)
                await enviar_telegram(mensagem)

        # Se o preço não mudou e SEND_NOTIFICATIONS é True, envia uma notificação
        elif SEND_NOTIFICATIONS:
            logging.info("🔔 O preço não mudou, mas a notificação será enviada devido à configuração.")
            mensagem = f"O preço atual é: R$ {preco_atual}"

            # Envia e-mail
            enviar_email(mensagem)

            # Envia Telegram (assíncrono)
            await enviar_telegram(mensagem)

# Função para rodar o agendamento
def agendar_monitoramento():
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Iniciando o monitoramento do produto...")
    
    # Agendamento para rodar a cada 6 horas
    schedule.every(6).hours.do(lambda: asyncio.run(monitorar()))

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    agendar_monitoramento()
