import os
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
KIE_API_KEY = os.getenv("KIE_API_KEY")

STICKERS_SHORT = ["CAACAgIAAxkBAAFAkF1pZC5-bjCQGO3vSDBxNs9uw47WkwACrRIAAmM-SEj3kkxB7sI7OjgE"]

def get_thinking_sticker(text: str):
    return random.choice(STICKERS_SHORT)

def ai_generate_lyrics(prompt):
    r = requests.post(
        "https://api.kie.ai/gemini-3-pro/v1/chat/completions",
        headers={"Authorization": f"Bearer {KIE_API_KEY}", "Content-Type": "application/json"},
        json={"messages":[{"role":"system","content":"Ты профессиональный автор песен. Пиши эмоционально, перед текстом добавляй короткий комментарий."},{"role":"user","content":prompt}]},
        timeout=90
    )
    return r.json()["choices"][0]["message"]["content"]

def build_app():
    app = Application.builder().token(BOT_TOKEN).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Привет! 🎵 Напиши что-нибудь, и я сделаю песню!")

    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        thinking = await update.message.reply_sticker(get_thinking_sticker(text))
        lyrics = ai_generate_lyrics(text)
        try: await thinking.delete()
        except: pass
        await update.message.reply_text(lyrics)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app
  
