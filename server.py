import os
from flask import Flask, request
from telegram import Update
from main import build_app

app = Flask(__name__)
tg_app = build_app()

@app.route("/health")
def health():
    return "ok", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.json, tg_app.bot)
    tg_app.update_queue.put_nowait(update)
    return "ok", 200

if __name__ == "__main__":
    tg_app.bot.set_webhook(os.getenv("WEBHOOK_URL"))
    tg_app.initialize()
    tg_app.start()
    app.run(host="0.0.0.0", port=8000)
  
