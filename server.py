from flask import Flask, request
from telegram import Update
from main import build_app
import os

app = Flask(__name__)
tg_app = build_app()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
tg_app.bot.set_webhook(WEBHOOK_URL)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    tg_app.update_queue.put(update)
    return "ok"

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
  
