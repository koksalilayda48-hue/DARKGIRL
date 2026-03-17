import logging
import time
import os
import re
from collections import defaultdict
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)
import openai

# ENV
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

# Küfür listesi
BAD_WORDS = ["salak", "aptal"]

# İzinli linkler
WHITELIST = ["youtube.com", "youtu.be"]

# Link regex
LINK_PATTERN = r"(https?://|www\.|t\.me/)"

# Spam sistemi
user_messages = defaultdict(list)
SPAM_LIMIT = 5
SPAM_TIME = 5

# Uyarı sistemi
warnings = defaultdict(int)

# Admin kontrol
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id

    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ Bu bot sadece gruplarda çalışır.")
        return

    await update.message.reply_text("🤖 Ultra bot aktif!")

# Mesaj kontrol
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type

    # 🎯 SADECE GRUP
    if chat_type == "private":
        return

    user = update.message.from_user
    user_id = user.id
    username = user.first_name
    text = update.message.text.lower()

    admin = await is_admin(update, context)

    # 🔗 LINK KONTROL
    if re.search(LINK_PATTERN, text):
        if not admin:
            if not any(site in text for site in WHITELIST):
                await update.message.delete()
                warnings[user_id] += 1

                await update.effective_chat.send_message(
                    f"🔗 {username} link yasak! Uyarı: {warnings[user_id]}"
                )
            return

    # 🔴 Küfür kontrol
    if any(word in text for word in BAD_WORDS):
        await update.message.delete()
        warnings[user_id] += 1

        await update.effective_chat.send_message(
            f"⚠️ {username} küfür etti! Uyarı: {warnings[user_id]}"
        )

    # 🔴 Spam kontrol
    now = time.time()
    user_messages[user_id] = [
        t for t in user_messages[user_id] if now - t < SPAM_TIME
    ]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > SPAM_LIMIT:
        await update.message.delete()
        await update.effective_chat.send_message(
            f"🚫 {username} spam yaptı!"
        )

    # 🚫 BAN SİSTEMİ
    if warnings[user_id] >= 3:
        try:
            await context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id
            )
            await update.effective_chat.send_message(
                f"🚫 {username} banlandı!"
            )
            return
        except:
            pass

    # 🧠 AI cevap
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Sen Türkçe konuşan, samimi ama saygılı bir asistansın. Kısa ve net cevap ver.",
                },
                {"role": "user", "content": text},
            ],
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

    except:
        await update.message.reply_text("⚠️ AI cevap veremedi.")

# MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Ultra bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
