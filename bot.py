import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from admin.models import db, BotStats, SearchQuery
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

async def log_command(update: Update, command: str, success: bool = True):
    """Логирование команды в базу данных"""
    try:
        stat = BotStats(
            command=command,
            user_id=update.effective_user.id,
            success=success
        )
        db.session.add(stat)
        db.session.commit()
    except Exception as e:
        logging.error(f"Ошибка при логировании команды: {e}")

async def log_search(update: Update, query: str, results_count: int):
    """Логирование поискового запроса в базу данных"""
    try:
        search = SearchQuery(
            query=query,
            user_id=update.effective_user.id,
            results_count=results_count
        )
        db.session.add(search)
        db.session.commit()
    except Exception as e:
        logging.error(f"Ошибка при логировании поиска: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = """
Привет! Я бот для получения новостей о криптовалютах 🚀
Доступные команды:
/news - получить последние новости о криптовалютах
/search <запрос> - поиск конкретной информации о криптовалютах
"""
    await update.message.reply_text(welcome_message)
    await log_command(update, "start")

async def get_crypto_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение последних новостей о криптовалютах"""
    try:
        with DDGS() as ddgs:
            results = ddgs.news(
                "cryptocurrency crypto bitcoin news",
                region="ru-ru",
                max_results=5
            )
            
            news_text = "📰 Последние новости о криптовалютах:\n\n"
            count = 0
            for result in results:
                news_text += f"🔹 {result['title']}\n"
                news_text += f"📝 {result['body'][:200]}...\n"
                news_text += f"🔗 {result['link']}\n\n"
                count += 1
                
            await update.message.reply_text(news_text)
            await log_command(update, "news")
            await log_search(update, "crypto news", count)
    except Exception as e:
        logging.error(f"Ошибка при получении новостей: {e}")
        await update.message.reply_text("Извините, произошла ошибка при получении новостей. Попробуйте позже.")
        await log_command(update, "news", success=False)

async def search_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск информации по запросу пользователя"""
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите поисковый запрос после команды /search")
        await log_command(update, "search", success=False)
        return

    query = ' '.join(context.args) + " cryptocurrency"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(
                query,
                region="ru-ru",
                max_results=3
            )
            
            search_text = f"🔍 Результаты поиска по запросу '{' '.join(context.args)}':\n\n"
            count = 0
            for result in results:
                search_text += f"📌 {result['title']}\n"
                search_text += f"📝 {result['body']}\n"
                search_text += f"🔗 {result['link']}\n\n"
                count += 1
                
            await update.message.reply_text(search_text)
            await log_command(update, "search")
            await log_search(update, ' '.join(context.args), count)
    except Exception as e:
        logging.error(f"Ошибка при поиске: {e}")
        await update.message.reply_text("Извините, произошла ошибка при поиске. Попробуйте позже.")
        await log_command(update, "search", success=False)

def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", get_crypto_news))
    application.add_handler(CommandHandler("search", search_crypto))

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 