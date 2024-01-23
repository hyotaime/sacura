from telegram import Update
from telegram.ext import ContextTypes
import os
from dotenv import load_dotenv
from src.log import logger
from src import database


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    load_dotenv()
    if str(chat_id) != os.environ.get('CHAT_ID'):
        return None
    logger.info(f"ChatID: {chat_id} - remove")
    # 입력 메시지에서 '/now'를 제외한 텍스트 추출
    ticker = update.message.text.replace('/remove', '').replace('@sacura_hirame_bot', '').strip().upper()
    if database.is_ticker_available(ticker):
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please enter available ticker."
        )
    else:
        await process_remove(ticker)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{ticker}: Remove success."
        )


async def r(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    load_dotenv()
    if str(chat_id) != os.environ.get('CHAT_ID'):
        return None
    logger.info(f"ChatID: {chat_id} - r")
    # 입력 메시지에서 '/n'를 제외한 텍스트 추출
    ticker = update.message.text.replace('/r', '').replace('@sacura_hirame_bot', '').strip().upper()
    if database.is_ticker_available(ticker):
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please enter available ticker."
        )
    else:
        await process_remove(ticker)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{ticker}: Remove success."
        )


async def process_remove(ticker: str):
    match ticker.split('.')[-1]:
        case 'KS':
            database.remove_kospi(ticker)
        case 'T':
            database.remove_nikkei(ticker)
        case _:
            database.remove_nasdaq(ticker)
