FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта
COPY . .

# Создание директории для логов
RUN mkdir -p logs

# Создание volume для базы данных
VOLUME /app/instance

# Запуск бота и админ-панели
CMD ["sh", "-c", "python bot.py & python run_admin.py"] 