# 🛒 Monitorador de Preços - Mercado Livre

Um sistema automatizado para monitorar preços de produtos no Mercado Livre, enviando alertas por e-mail e Telegram, e atualizando o menor preço registrado.

---

## 🚀 Funcionalidades

- 📉 Monitora múltiplos produtos simultaneamente
- 📬 Envia notificações via E-mail e Telegram
- 🕐 Executado automaticamente via GitHub Actions (horários definidos)
- 💾 Armazena o menor preço registrado de forma segura
- 🛠️ Modo Debug e verificação de status ativa por hora

---

## 🧠 Como funciona

1. O script extrai o preço atual dos produtos a partir da URL fornecida.
2. Compara com o menor preço já salvo localmente.
3. Se for menor (ou se estiver em modo debug), envia notificação e salva o novo valor.
4. A cada hora, verifica se o produto ainda está acessível e envia mensagem de status.

---

## 🖥️ Rodando localmente

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seuusuario/nome-do-repositorio.git
   cd nome-do-repositorio
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Ou venv\Scripts\activate no Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis no `.env`**
   Copie o exemplo abaixo:
   ```env
   TELEGRAM_TOKEN=seu_token
   TELEGRAM_CHAT_ID=seu_chat_id
   EMAIL_USER=seu_email@gmail.com
   EMAIL_PASS=sua_senha_de_app
   EMAIL_TO=destinatario@gmail.com
   PRODUCT_URLS=https://produto1,...,https://produtoN
   DEBUG_MODE=False
   SEND_NOTIFICATIONS=True
   SEND_STATUS_TELEGRAM=True
   ```

5. **Execute o script manualmente**
   ```bash
   python rodar.py
   ```

---

## ⚙️ Executando via GitHub Actions

- O agendamento no arquivo `monitoramento.yml` já roda automaticamente nos horários definidos (Brasília: 00h, 06h, 12h, 18h).
- Os menores preços são versionados e atualizados automaticamente no repositório (pasta `precos/`).

---

## 📦 Dependências principais

- `requests`
- `beautifulsoup4`
- `python-dotenv`
- `schedule`
- `python-telegram-bot`
- `pytz`

Instale com:
```bash
pip install -r requirements.txt
```

---

## 📁 Estrutura do Projeto

```
.
├── main.py              # Script principal (agendado e monitorado)
├── rodar.py             # Execução manual
├── .env                 # Variáveis de ambiente (não versionar)
├── precos/              # Armazena os menores preços
├── monitoramento.yml    # GitHub Actions (CI)
├── requirements.txt     # Lista de dependências
└── README.md
```

---

## 🛡️ Segurança

- Nunca compartilhe seu `.env` com credenciais.
- Use **senhas de app** (ex: no Gmail).
- No GitHub, use `secrets` para dados sensíveis e `vars` para configs públicas.

---

## 📄 Licença

[MIT License](LICENSE)
