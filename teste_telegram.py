import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

# Carrega o .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def enviar_telegram_teste():
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🚀 Teste de mensagem via Telegram Bot!")
        print("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        print("❌ Erro ao enviar mensagem no Telegram:", e)

if __name__ == "__main__":
    asyncio.run(enviar_telegram_teste())
