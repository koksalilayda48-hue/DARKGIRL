from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import openai
import logging

# -----------------------------
# Sabitler (direkt kodda, Render için test)
# -----------------------------
BOT_TOKEN = "8691448778:AAHYxH0rmOw-TWOV_x4tEo17ql9rStN4Irc"
OPENAI_API_KEY = "00c0e044-7725-4008-99f5-b6cb99f36443"

openai.api_key = OPENAI_API_KEY

# -----------------------------
# Logging (hata takibi için)
# -----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# -----------------------------
# Komutlar
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot başlatıldığında /start komutu."""
    await update.message.reply_text("Merhaba! Yapay zeka botuna hoş geldiniz.")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OpenAI üzerinden cevap verir. Kullanım: /ask <soru>"""
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("Lütfen bir soru yazın.")
        return
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=question,
            max_tokens=150
        )
        answer = response.choices[0].text.strip()
        await update.message.reply_text(answer)
    except Exception as e:
        logger.error(f"Hata oluştu: {e}")
        await update.message.reply_text(f"Hata oluştu: {e}")

# -----------------------------
# Botu başlat
# -----------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Komutları ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask))

    print("Bot çalışıyor...")
    app.run_polling()
