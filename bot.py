import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = """
Привет! Я бот для получения новостей о криптовалютах 🚀
Доступные команды:
/news - получить последние новости о криптовалютах
/search <запрос> - поиск конкретной информации о криптовалютах
"""
    await update.message.reply_text(welcome_message)

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
            for result in results:
                news_text += f"🔹 {result['title']}\n"
                news_text += f"📝 {result['body'][:200]}...\n"
                news_text += f"🔗 {result['link']}\n\n"
                
            await update.message.reply_text(news_text)
    except Exception as e:
        logging.error(f"Ошибка при получении новостей: {e}")
        await update.message.reply_text("Извините, произошла ошибка при получении новостей. Попробуйте позже.")

async def search_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск информации по запросу пользователя"""
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите поисковый запрос после команды /search")
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
            for result in results:
                search_text += f"📌 {result['title']}\n"
                search_text += f"📝 {result['body']}\n"
                search_text += f"🔗 {result['link']}\n\n"
                
            await update.message.reply_text(search_text)
    except Exception as e:
        logging.error(f"Ошибка при поиске: {e}")
        await update.message.reply_text("Извините, произошла ошибка при поиске. Попробуйте позже.")

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