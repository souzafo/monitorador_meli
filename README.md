# 🛒 Monitorador de Preços - Mercado Livre

Um sistema automatizado para monitorar preços de produtos no Mercado Livre, enviando alertas por e-mail e Telegram, e atualizando o menor preço registrado.

---

## 🚀 Funcionalidades

- 📉 Monitora múltiplos produtos simultaneamente
- 📬 Envia notificações via E-mail e Telegram
- 🕐 Executado automaticamente via GitHub Actions (horários definidos)
- 💾 Armazena o menor preço registrado de forma segura
- 🛠️ Modo Debug e verificação de status ativa por hora
- 🧠 Comportamento inteligente:
  - Telegram: mostra sempre o preço atual e comparações
  - E-mail: enviado **somente** quando o preço atual for **menor** que o menor registrado

---

## 🧠 Como funciona

1. O script extrai o preço atual dos produtos a partir da URL fornecida.
2. Compara com o menor preço já salvo localmente.
3. Se for menor (ou se estiver em modo debug), envia notificação e salva o novo valor.
4. A cada hora, verifica se o produto ainda está acessível e envia mensagem de status.

---

## 🖥️ Rodando localmente

1. **Clone o repositório**
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Ou venv\Scripts\activate no Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure seu arquivo `.env` com as variáveis necessárias.
5. Rode o script:
   ```bash
   python rodar.py
   ```

---

## ☁️ Executando via GitHub Actions

O GitHub Actions executa o monitoramento automaticamente 4 vezes ao dia (00h, 06h, 12h, 18h no horário de Brasília). 

Além disso, se houver alteração no menor preço, um commit automático será feito na pasta `precos/`.

---

## 🔧 Variáveis de ambiente (.env)

```env
# 🔐 Credenciais
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
EMAIL_USER=...
EMAIL_PASS=...

# 🛍️ Produtos separados por vírgula
PRODUCT_URLS=https://produto1,...,https://produtoN

# 📩 Destinatário do e-mail
EMAIL_TO=voce@email.com

# ⚙️ Configurações
DEBUG_MODE=False
SEND_NOTIFICATIONS=True
SEND_STATUS_TELEGRAM=True
```

---

## 📁 Estrutura de Diretórios

```
.
├── precos/               # Armazena os menores preços registrados
├── main.py               # Script principal
├── rodar.py              # Executa monitoramento local
├── requirements.txt      # Dependências do projeto
├── .env                  # Variáveis de ambiente
└── .github/
    └── workflows/
        └── monitoramento.yml  # Agendamento GitHub Actions
```

---

## 📜 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
