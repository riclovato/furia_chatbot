import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from bot.handlers.matches import matches_handler, format_matches_message
from telegram import Update
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.handlers.matches import store_matches


@pytest.fixture
def mock_update():
    update = AsyncMock(spec=Update)
    update.message = AsyncMock()
    update.callback_query = None  # Importante para evitar chamadas indesejadas
    return update

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.args = []
    context.job_queue = MagicMock()
    return context

@pytest.mark.asyncio
async def test_matches_handler_with_matches(mock_update, mock_context):
    mock_matches = [{
        'opponent': 'Team Liquid',
        'event': 'BLAST Premier 2025',
        'time': '30/04/2025 19:00',
        'link': 'https://draft5.gg/fake-match',
        'format': 'BO3'
    }]
    
    with patch('bot.handlers.matches.matches_scraper.get_furia_matches', return_value=mock_matches):
        await matches_handler(mock_update, mock_context)
        
        # Verifica o número de chamadas
        assert mock_update.message.reply_text.await_count == 1
        
        args, kwargs = mock_update.message.reply_text.call_args
        assert 'Team Liquid' in args[0]
        assert 'BO3' in args[0]

@pytest.mark.asyncio
async def test_matches_handler_no_matches(mock_update, mock_context):
    with patch('bot.handlers.matches.matches_scraper.get_furia_matches', return_value=[]):
        await matches_handler(mock_update, mock_context)
        
        args, kwargs = mock_update.message.reply_text.call_args
        assert 'Nenhum jogo agendado' in args[0]

@pytest.mark.asyncio
async def test_matches_handler_force_update(mock_update, mock_context):
    mock_context.args = ['force']
    
    with patch('bot.handlers.matches.matches_scraper.get_furia_matches') as mock_scraper:
        mock_scraper.return_value = []
        await matches_handler(mock_update, mock_context)
        mock_scraper.assert_called_once_with(force_update=True)

def test_format_matches_message():
    matches = [{
        'opponent': 'Natus Vincere',
        'event': 'IEM Katowice 2025',
        'time': '01/05/2025 20:00',
        'link': 'https://draft5.gg/another-match',
        'format': 'BO3'
    }]
    
    message, _ = format_matches_message(matches)
    assert 'BO3' in message
    assert 'IEM Katowice 2025' in message