FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта
COPY bot.py .
COPY .env .

# Запуск бота
CMD ["python", "bot.py"] 