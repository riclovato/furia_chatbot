import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

# Carrega variáveis de ambiente
load_dotenv()

async def start(update, context):
    await update.message.reply_text("Olá fã da FURIA! Use /matches ou /players.")

def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()