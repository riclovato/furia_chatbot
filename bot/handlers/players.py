import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, CallbackQueryHandler
from datetime import datetime

logger = logging.getLogger(__name__)


FURIA_PLAYERS = [
   {
        'id': 1,
        'name': 'KSCERATO',
        'full_name': 'Kaike Cerato',
        'age': 25,
        'nationality': 'Brazil',
        'role': 'Rifler',
        'join_date': '2018-02-21',
        'photo_url': 'https://img-cdn.hltv.org/playerbodyshot/U6t0j2bJDKUR3mTI8rIqv7.png?ixlib=java-2.1.0&w=400&s=b5257c378b8122f415f21985855e95ca'
    },
    {
        'id': 2,
        'name': 'yuurih',
        'full_name': 'Yuri Santos',
        'age': 25,
        'nationality': 'Brazil',
        'role': 'Rifler',
        'join_date': '2018-11-23',
        'photo_url': 'https://img-cdn.hltv.org/playerbodyshot/i6UGhkYxrhutAOmWZT0-8O.png?ixlib=java-2.1.0&w=400&s=2cd696f6ff4baf5680a43d537214b6eb'
    },
    {
        'id': 3,
        'name': 'FalleN',
        'full_name': 'Gabriel Toledo',
        'age': 33,
        'nationality': 'Brazil',
        'role': 'IGL/AWPer',
        'join_date': '2023-07-01',
        'photo_url': 'https://img-cdn.hltv.org/playerbodyshot/Wf26SO_o8nvnsLh0AqZXc5.png?ixlib=java-2.1.0&w=400&s=36b7189a4ae7b020d0acb087fd44777a'
    },
    {
        'id': 4,
        'name': 'molodoy',
        'full_name': 'Danil Golubenko',
        'age': 20,
        'nationality': 'Kazakhstan',
        'role': 'AWPer',
        'join_date': '2025-05-11',
        'photo_url': 'https://img-cdn.hltv.org/playerbodyshot/qNyAd_xVHTTmbCAKPx-jPk.png?ixlib=java-2.1.0&w=400&s=b128ede878e462107c70590202b14139'
    },
    {
        'id': 5,
        'name': 'YEKINDAR',
        'full_name': 'Mareks Gaļinskis',
        'age': 25,
        'nationality': 'Latvia',
        'role': 'Entry Fragger',
        'join_date': '2025-04-22',
        'photo_url': 'https://img-cdn.hltv.org/playerbodyshot/rRclDPBXIMxFv2fv0dV0J0.png?ixlib=java-2.1.0&w=400&s=2b0f6209ca40efa081852b9d1d8e01c1'
    }
]



async def team_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /team - mostra o elenco atual"""
    try:
        # Cria teclado inline com os jogadores
        keyboard = [
            [InlineKeyboardButton(player['name'], callback_data=f"player_{player['id']}")]
            for player in FURIA_PLAYERS
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🟡⚫ *Elenco Atual da FURIA* ⚫🟡\n\n"
            "Selecione um jogador para ver mais informações:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Erro no team_handler: {str(e)}")
        await update.message.reply_text(
            "⚠️ Ocorreu um erro ao buscar o elenco. Tente novamente mais tarde.",
            parse_mode="Markdown"
        )

async def button_handler(update: Update, context: CallbackContext):
    """Handler para os botões inline"""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data.startswith("player_"):
            player_id = int(query.data.split("_")[1])
            player = next(p for p in FURIA_PLAYERS if p['id'] == player_id)
            
            # Calcula tempo no time
            join_date = datetime.strptime(player['join_date'], '%Y-%m-%d')
            time_in_team = (datetime.now() - join_date).days // 365
            
            response = (
                f"🐅 *{player['name']} ({player['full_name']})*\n\n"
                f"🌎 Nacionalidade: {player['nationality']}\n"
                f"🎂 Idade: {player['age']} anos\n"
                f"🎮 Função: {player['role']}\n"
                f"📅 No time há: {time_in_team} {'ano' if time_in_team == 1 else 'anos'}\n\n"
                f"📸 [Foto do jogador]({player['photo_url']})"
            )
            
            await query.edit_message_text(
                text=response,
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Erro no button_handler: {str(e)}")
        await query.edit_message_text(
            text="⚠️ Ocorreu um erro ao buscar informações. Tente novamente.",
            parse_mode="Markdown"
        )

