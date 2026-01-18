import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Токен берём из переменной среды
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Инициализация приложения
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# ======================
# Функции бота
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Привет! Я ваш музыкальный бот 🎵\nВыберите действие:"
    keyboard = [
        [InlineKeyboardButton("🎹 Новая песня", callback_data="new_song")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("🔗 Рефы", callback_data="ref")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "new_song":
        await generate_song(query, context)
    elif data == "balance":
        await query.edit_message_text("Ваш баланс: 100 кредитов 💳")
    elif data == "ref":
        await query.edit_message_text("Ваш реф-код: REF12345 🔗")

async def generate_song(query, context):
    await query.edit_message_text("Думающий зверёк обрабатывает ваш запрос… 🐹")
    
    # Здесь твоя интеграция с Kie AI для генерации текста песни
    # Пример заглушки:
    await asyncio.sleep(2)  # имитация работы
    song_text = "🎵 Ваш трек готов! 🎵\nНазвание: Моя песня\nЖанр: Поп"
    
    # Второй трек в подарок
    song_text += "\n🎁 Второй трек в подарок!\nНазвание: Подарочный хит"

    await query.edit_message_text(song_text)

# ======================
# Хэндлеры
# ======================
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# ======================
# Основной запуск
# ======================
if __name__ == "__main__":
    telegram_app.run_polling()

