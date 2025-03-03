import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update
from telegram.ext import ContextTypes
import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import start, get_crypto_news, search_crypto

@pytest.mark.asyncio
async def test_start_command():
    # Подготовка тестовых данных
    update = AsyncMock(spec=Update)
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    
    # Вызов тестируемой функции
    await start(update, context)
    
    # Проверка результата
    update.message.reply_text.assert_called_once()
    assert "Привет!" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_get_crypto_news():
    update = AsyncMock(spec=Update)
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    
    # Мокаем DDGS для тестирования без реальных API-вызовов
    mock_news = [
        {
            'title': 'Test News',
            'body': 'Test Body',
            'link': 'https://test.com'
        }
    ]
    
    with patch('bot.DDGS') as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.news.return_value = mock_news
        await get_crypto_news(update, context)
        
        update.message.reply_text.assert_called_once()
        response_text = update.message.reply_text.call_args[0][0]
        assert 'Test News' in response_text
        assert 'Test Body' in response_text
        assert 'https://test.com' in response_text

@pytest.mark.asyncio
async def test_search_crypto():
    update = AsyncMock(spec=Update)
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = ['bitcoin']
    
    mock_results = [
        {
            'title': 'Bitcoin Info',
            'body': 'Bitcoin Description',
            'link': 'https://bitcoin-info.com'
        }
    ]
    
    with patch('bot.DDGS') as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = mock_results
        await search_crypto(update, context)
        
        update.message.reply_text.assert_called_once()
        response_text = update.message.reply_text.call_args[0][0]
        assert 'Bitcoin Info' in response_text
        assert 'Bitcoin Description' in response_text
        assert 'https://bitcoin-info.com' in response_text

@pytest.mark.asyncio
async def test_search_crypto_no_args():
    update = AsyncMock(spec=Update)
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = []
    
    await search_crypto(update, context)
    
    update.message.reply_text.assert_called_once_with(
        "Пожалуйста, укажите поисковый запрос после команды /search"
    ) 