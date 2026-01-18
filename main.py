import os
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ===== НАСТРОЙКИ =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
KIE_API_KEY = os.getenv("KIE_API_KEY")
KIE_URL = "https://api.kie.ai/gemini-3-pro/v1/chat/completions"

# ===== СТИКЕРЫ =====
STICKERS_SHORT = [
    "CAACAgIAAxkBAAFAkF1pZC5-bjCQGO3vSDBxNs9uw47WkwACrRIAAmM-SEj3kkxB7sI7OjgE",
]
STICKERS_MEDIUM = [
    "CAACAgIAAxkBAAFAkGVpZC85SqT4hr8HkTkGJ9jyS99kTgAC2wwAArL_AAFKYuoEPmlC2wg4BA",
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
    else:
        return random.choice(STICKERS_LONG)

# ===== КНОПКИ =====
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
         InlineKeyboardButton("🎤 Рэп / хип-хоп", callback_data="genre_rap")],
        [InlineKeyboardButton("💃 Диско 90-х", callback_data="genre_disco90"),
         InlineKeyboardButton("🎸 Рок", callback_data="genre_rock")],
        [InlineKeyboardButton("🎷 Шансон", callback_data="genre_chanson"),
         InlineKeyboardButton("🌌 Транс", callback_data="genre_trance")],
        [InlineKeyboardButton("🎻 Классика", callback_data="genre_classic"),
         InlineKeyboardButton("🔥 Трэп", callback_data="genre_trap")],
        [InlineKeyboardButton("✍️ Свой стиль", callback_data="genre_custom")]
    ])

def buy_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Оплата через CryptoBot", callback_data="buy_crypto")],
        [InlineKeyboardButton("⭐ Telegram Stars", callback_data="buy_stars")]
    ])

def crypto_packages():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("499 ₽   →   1 песня", callback_data="pack_1")],
        [InlineKeyboardButton("899 ₽   →   3 песни", callback_data="pack_3")],
        [InlineKeyboardButton("1499 ₽ →   10 песен", callback_data="pack_10")]
    ])

# ===== ИИ =====
def ai_generate_lyrics(prompt):
    r = requests.post(
        KIE_URL,
        headers={"Authorization": f"Bearer {KIE_API_KEY}", "Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": "Ты профессиональный автор песен. Пиши живо, эмоционально, как в Bro Hit. Перед текстом всегда добавляй короткий комментарий-реакцию."},
                {"role": "user", "content": prompt}
            ]
        },
        timeout=90
    )
    return r.json()["choices"][0]["message"]["content"]

# ===== СТАРТ =====
async def start_base(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["state"] = "reason"
    await update.message.reply_text(
        "Какую песню ты хотел бы создать? Можешь выбрать из списка или написать свой вариант.",
        reply_markup=reasons_menu()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "друг"
    await update.message.reply_text(f"Привет, {user_name}! 👋")
    await start_base(update, context)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_base(update, context)

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери способ оплаты\nдля покупки песен:", reply_markup=buy_menu())

async def ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    await update.message.reply_text(f"👥 Реферальная программа\n\nТвоя ссылка:\n{ref_link}")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Помощь\n\n1️⃣ Выбери повод\n2️⃣ Выбери жанр\n3️⃣ Опиши идею\n\n🎶 Бот сделает песню"
    )

# ===== CALLBACK =====
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    msg = q.message

    if data.startswith("reason_"):
        if data == "reason_custom":
            context.user_data["state"] = "custom_reason"
            await msg.reply_text("✍️ Напиши свой повод")
            return
        reason_map = {
            "birthday": "🎂 День рождения", "newyear": "🎄 Новый год",
            "holiday": "🎉 Праздник", "love": "❤️ Признание",
            "wedding": "💍 Свадьба", "joke": "😂 Розыгрыш",
            "support": "🤝 Поддержка"
        }
        key = data.replace("reason_", "")
        context.user_data["reason"] = reason_map[key]
        context.user_data["state"] = "genre"
        await msg.reply_text(f"Тип песни: {context.user_data['reason']}")
        await msg.reply_text("🎵 В каком жанре делаем песню?\nМожешь выбрать из списка или написать свой.", reply_markup=genres_menu())
    elif data.startswith("genre_"):
        if data == "genre_custom":
            context.user_data["state"] = "custom_genre"
            await msg.reply_text("✍️ Опиши стиль")
            return
        genre_map = {
            "pop": "🎶 Поп", "rap": "🎤 Рэп / хип-хоп", "disco90": "💃 Диско 90-х",
            "rock": "🎸 Рок", "chanson": "🎷 Шансон", "trance": "🌌 Транс",
            "classic": "🎻 Классика", "trap": "🔥 Трэп"
        }
        key = data.replace("genre_", "")
        context.user_data["genre"] = genre_map[key]
        context.user_data["state"] = "description"
        await msg.reply_text(f"Тип песни: {context.user_data['reason']}")
        await msg.reply_text(f"Жанр песни: {context.user_data['genre']}")
        await msg.reply_text("💬 Напиши всё, что может вдохновить:")

# ===== TEXT =====
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    state = context.user_data.get("state")

    if state == "custom_reason":
        context.user_data["reason"] = f"✍️ {text}"
        context.user_data["state"] = "genre"
        await update.message.reply_text(f"Тип песни: {context.user_data['reason']}")
        await update.message.reply_text("Выбери жанр 👇", reply_markup=genres_menu())
    elif state == "custom_genre":
        context.user_data["genre"] = f"🎧 {text}"
        context.user_data["state"] = "description"
        await update.message.reply_text(f"Тип песни: {context.user_data['reason']}")
        await update.message.reply_text(f"Жанр песни: {context.user_data['genre']}")
    elif state == "description":
        thinking = await update.message.reply_sticker(random.choice(STICKERS_SHORT))
        prompt = f"Повод: {context.user_data['reason']}\nЖанр: {context.user_data['genre']}\n\n{text}"
        lyrics = ai_generate_lyrics(prompt)
        try:
            await thinking.delete()
        except:
            pass
        await update.message.reply_text(lyrics)

# ===== ЗАПУСК =====
async def setup_commands(app):
    await app.bot.set_my_commands([
        BotCommand("new_song", "🎵 Новая песня"),
        BotCommand("buy", "🛒 Купить"),
        BotCommand("ref", "👥 Реферал"),
        BotCommand("help", "❓ Помощь"),
        BotCommand("restart", "🔁 Перезапустить бота"),
    ])

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new_song", start_base))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("ref", ref))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.post_init = setup_commands
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
         
