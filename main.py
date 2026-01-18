import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fastapi import FastAPI, Request
import uvicorn

# --- Переменные окружения ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PUBLIC_URL = os.environ.get("KOYEB_PUBLIC_DOMAIN")

if not BOT_TOKEN or not PUBLIC_URL:
    raise Exception("BOT_TOKEN и KOYEB_PUBLIC_DOMAIN должны быть заданы в настройках Koyeb")

# --- FastAPI приложение (для webhook) ---
app = FastAPI()

# --- Telegram Application ---
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Команды бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает через webhook на Koyeb!")

telegram_app.add_handler(CommandHandler("start", start))

# --- Webhook endpoint для Koyeb ---
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return {"ok": True}

# --- Настройка webhook при старте ---
async def set_webhook():
    url = f"https://{PUBLIC_URL}/{BOT_TOKEN}"
    await telegram_app.bot.set_webhook(url)

# --- Запуск приложения ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    uvicorn.run(app, host="0.0.0.0", port=8000)
  
