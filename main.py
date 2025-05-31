import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация логирования
logging.basicConfig(level=logging.INFO)

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-секретарь Sunesty. Готов к работе!")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = ' '.join(context.args)
    if task:
        with open("tasks.txt", "a") as f:
            f.write(task + "\n")
        await update.message.reply_text(f"Задача добавлена: {task}")
    else:
        await update.message.reply_text("Пожалуйста, укажи текст задачи после команды.")

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists("tasks.txt"):
        with open("tasks.txt", "r") as f:
            tasks = f.read().strip()
        if tasks:
            await update.message.reply_text("Твои задачи:\n" + tasks)
        else:
            await update.message.reply_text("У тебя пока нет задач.")
    else:
        await update.message.reply_text("Файл задач не найден.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        answer = response["choices"][0]["message"]["content"]
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при генерации ответа.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("задача", add_task))
    app.add_handler(CommandHandler("задачи", show_tasks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
