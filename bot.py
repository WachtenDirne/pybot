from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Токен бота и ID чата
TOKEN = "7713211792:AAHz4aXX6vJBUB04c6TDSfTAxAZwmhdAe8c"
GROUP_ID = -1002388896615

# Варианты завтраков
BREAKFASTS = [
    "Овсяночка 🥣",
    "Вкуснейший омлет 🍳",
    "Яичница с беконом 🥓",
    "Бутерброды 🥪",
    "Свой вариант ✍️"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    keyboard = [
        [InlineKeyboardButton(option, callback_data=option)] for option in BREAKFASTS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Солнышко моё, выбери, что ты хочешь на завтрак:", reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки."""
    query = update.callback_query
    await query.answer()
    selected_option = query.data

    # Сохраняем выбранный завтрак и переходим к запросу дополнений
    context.user_data['selected_breakfast'] = selected_option
    await query.edit_message_text(
        f"Ты выбрала: {selected_option}. Напиши, что добавить к завтраку:"
    )
    context.user_data['waiting_for_addition'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений."""
    if context.user_data.get('waiting_for_addition'):
        # Получаем дополнения
        addition = update.message.text
        selected_breakfast = context.user_data.get('selected_breakfast', 'Неизвестно')

        # Отправляем сообщение в группу
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"🌟 Завтрак выбран: {selected_breakfast}\nДополнения: {addition}"
        )

        # Подтверждаем выбор пользователю
        await update.message.reply_text(
            f"Спасибо! Ты выбрала: {selected_breakfast}.\nС дополнением: {addition}"
        )

        # Отправляем пожелания
        await update.message.reply_text(
            "Я люблю тебя, котёночек ❤️"
        )

        # Очищаем данные
        context.user_data['waiting_for_addition'] = False
        context.user_data['selected_breakfast'] = None

def main():
    """Главная функция."""
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск Telegram бота
    keep_alive()  # Запускаем Flask для "Keep Alive"
    application.run_polling()

if __name__ == "__main__":
    main()
