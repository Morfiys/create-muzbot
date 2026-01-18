import os
import uuid
import requests
import asyncio

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ================== ENV ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
KIE_API_KEY = os.getenv("KIE_API_KEY")

# ================== API ==================
KIE_GENERATE_URL = "https://api.kie.ai/api/v1/suno/generate"

# ⚠️ ЗАМЕНИ ПОТОМ на реальный домен Koyeb
CALLBACK_BASE_URL = "https://YOUR_KOYEB_URL"

# ================== APP ==================
app = FastAPI()
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Храним кто запросил генерацию
TASKS = {}

# ================== TELEGRAM ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Привет!\n\n"
        "Отправь команду:\n"
        "/gen текст песни"
    )

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Напиши текст после /gen")
        return

    prompt = " ".join(context.args)
    chat_id = update.effective_chat.id

    task_id = str(uuid.uuid4())
    TASKS[task_id] = chat_id

    payload = {
        "model": "V4_5",
        "prompt": prompt,
        "callbackUrl": f"{CALLBACK_BASE_URL}/callback/{task_id}"
    }

    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(KIE_GENERATE_URL, json=payload, headers=headers)

    if r.status_code != 200:
        await update.message.reply_text("❌ Ошибка запуска генерации")
        return

    await update.message.reply_text("⏳ Генерирую трек, подожди...")

# ================== CALLBACK ==================
@app.post("/callback/{task_id}")
async def callback(task_id: str, request: Request):
    data = await request.json()

    if task_id not in TASKS:
        return {"status": "unknown task"}

    chat_id = TASKS[task_id]

    # Ждём финальный callback
    if data.get("callbackType") != "complete":
        return {"status": "ok"}

    audio_url = data["data"]["audioUrl"]

    async def send_audio():
        await telegram_app.bot.send_audio(
            chat_id=chat_id,
            audio=audio_url,
            caption="🎶 Готово!"
        )

    asyncio.create_task(send_audio())
    return {"status": "sent"}

# ================== STARTUP ==================
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("gen", gen))

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()

@app.on_event("shutdown")
async def shutdown():
    await telegram_app.stop()
    await telegram_app.shutdown()
    
import threading
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

def run_bot():
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
        
