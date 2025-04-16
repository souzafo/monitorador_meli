import os
import asyncio
from dotenv import load_dotenv
from main import monitorar, verificar_status

# Carrega variáveis do .env
load_dotenv()

print("🚀 Verificando se variáveis foram carregadas...\n")

# Exibir variáveis principais
print("TELEGRAM_TOKEN:", "✔️" if os.getenv("TELEGRAM_TOKEN") else "❌")
print("TELEGRAM_CHAT_ID:", "✔️" if os.getenv("TELEGRAM_CHAT_ID") else "❌")
print("EMAIL_USER:", os.getenv("EMAIL_USER") or "❌")
print("EMAIL_PASS:", "✔️" if os.getenv("EMAIL_PASS") else "❌")
print("EMAIL_TO:", os.getenv("EMAIL_TO") or "❌")
print("DEBUG_MODE:", os.getenv("DEBUG_MODE"))
print("SEND_NOTIFICATIONS:", os.getenv("SEND_NOTIFICATIONS"))
print("SEND_STATUS_TELEGRAM:", os.getenv("SEND_STATUS_TELEGRAM"))

urls = os.getenv("PRODUCT_URLS", "").split(",")
print(f"\n🛒 Produtos para monitorar: {len(urls)} encontrados")
for i, url in enumerate(urls, start=1):
    print(f"  {i}. {url.strip()[:80]}...")

print("\n🚀 Iniciando monitoramento agora...\n")

# Executa monitoramento e verificação de status
asyncio.run(monitorar())
verificar_status()
