import os
import random
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
KIE_API_KEY = os.getenv("KIE_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

KIE_URL = "https://api.kie.ai/gemini-3-pro/v1/chat/completions"

STICKERS_SHORT = [
    "CAACAgIAAxkBAAFAkF1pZC5-bjCQGO3vSDBxNs9uw47WkwACrRIAAmM-SEj3kkxB7sI7OjgE",
    "CAACAgIAAxkBAAFAkGNpZC7dlW9bmugdkDPxkqFI2O2oXgACmw4AAhJp0UjTJWW13JUuJzgE",
]

STICKERS_MEDIUM = [
    "CAACAgIAAxkBAAFAkGVpZC85SqT4hr8HkTkGJ9jyS99kTgAC2wwAArL_AAFKYuoEPmlC2wg4BA",
    "CAACAgIAAxkBAAFAkGhpZC-nW0PeUnQJxrsiavi6HoT1TwACLwEAAvcCyA8H6pkHXqjshDgE",
]

STICKERS_LONG = [
    "CAACAgIAAxkBAAFAjZNpY_STcXRsy6Em-yA2duH9cEmpmAACiQoAAnFuiUvTl1zojCsDsDgE",
]

def get_thinking_sticker(text: str):
    l = len(text)
    if l < 40:
        return random.choice(STICKERS_SHORT)
    elif l < 120:
        return random.choice(STICKERS_MEDIUM)
    return random.choice(STICKERS_LONG)

def reasons_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎂 День рождения", callback_data="reason_birthday"),
         InlineKeyboardButton("🎄 Новый год", callback_data="reason_newyear")],
        [InlineKeyboardButton("🎉 Праздник", callback_data="reason_holiday"),
         InlineKeyboardButton("❤️ Признание", callback_data="reason_love")],
        [InlineKeyboardButton("💍 Свадьба", callback_data="reason_wedding"),
         InlineKeyboardButton("😂 Розыгрыш", callback_data="reason_joke")],
        [InlineKeyboardButton("🤝 Поддержка", callback_data="reason_support"),
         InlineKeyboardButton("✍️ Свой повод", callback_data="reason_custom")],
    ])

def genres_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎶 Поп", callback_data="genre_pop"),
         InlineKeyboardButton("🎤 Рэп", callback_data="genre_rap")],
        [InlineKeyboardButton("💃 Диско 90-х", callback_data="genre_disco90"),
         InlineKeyboardButton("🎸 Рок", callback_data="genre_rock")],
        [InlineKeyboardButton("🎷 Шансон", callback_data="genre_chanson"),
         InlineKeyboardButton("🌌 Транс", callback_data="genre_trance")],
        [InlineKeyboardButton("🎻 Классика", callback_data="genre_classic"),
         InlineKeyboardButton("🔥 Трэп", callback_data="genre_trap")],
        [InlineKeyboardButton("✍️ Свой стиль", callback_data="genre_custom")],
    ])

def ai_generate_lyrics(prompt):
    r = requests.post(
        KIE_URL,
        headers={
            "Authorization": f"Bearer {KIE_API_KEY}",
            "Content-Type": "application/json",
        },
        json={"messages": [
            {"role": "system", "content": "Ты профессиональный автор песен."},
            {"role": "user", "content": prompt}
        ]},
        timeout=90
    )
    return r.json()["choices"][0]["message"]["content"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["state"] = "reason"
    await update.message.reply_text("Выбери повод 👇", reply_markup=reasons_menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data.startswith("reason_"):
        context.user_data["reason"] = data.replace("reason_", "")
        context.user_data["state"] = "genre"
        await q.message.reply_text("Выбери жанр 👇", reply_markup=genres_menu())

    elif data.startswith("genre_"):
        context.user_data["genre"] = data.replace("genre_", "")
        context.user_data["state"] = "description"
        await q.message.reply_text("Опиши идею песни ✍️")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") == "description":
        thinking = await update.message.reply_sticker(get_thinking_sticker(update.message.text))
        prompt = f"{context.user_data['reason']} / {context.user_data['genre']}\n{update.message.text}"
        lyrics = ai_generate_lyrics(prompt)
        await thinking.delete()
        await update.message.reply_text(lyrics)

def build_app():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app
      
