from telegram import Update
from telegram.ext import ContextTypes
from src.log import logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info(f"ChatID: {chat_id} - start")
    await context.bot.send_message(
        chat_id=chat_id,
        text="I'm S.A.C.U.R.A\n"
             "Stock Analysis Crawler Using Requests and API.\n"
    )
