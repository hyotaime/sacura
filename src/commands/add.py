from telegram import Update
from telegram.ext import ContextTypes
import os
from dotenv import load_dotenv
from src.log import logger
from src import database


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    load_dotenv()
    if str(chat_id) != os.environ.get('CHAT_ID'):
        return None
    logger.info(f"ChatID: {chat_id} - add")
    # 입력 메시지에서 '/now'를 제외한 텍스트 추출
    ticker = update.message.text.replace('/add', '').replace('@sacura_hirame_bot', '').strip().upper()
    if database.is_ticker_available(ticker):
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please enter available ticker."
        )
    else:
        message = await process_add(ticker)
        await context.bot.send_message(
            chat_id=chat_id,
            text=message
        )


async def a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    load_dotenv()
    if str(chat_id) != os.environ.get('CHAT_ID'):
        return None
    logger.info(f"ChatID: {chat_id} - a")
    # 입력 메시지에서 '/n'를 제외한 텍스트 추출
    ticker = update.message.text.replace('/a', '').replace('@sacura_hirame_bot', '').strip().upper()
    if database.is_ticker_available(ticker):
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please enter available ticker."
        )
    else:
        message = await process_add(ticker)
        await context.bot.send_message(
            chat_id=chat_id,
            text=message
        )


async def process_add(ticker: str):
    if '.' not in ticker:
        return database.set_nasdaq(ticker)
    else:
        match ticker.split('.')[-1]:
            case 'KS':
                return database.set_kospi(ticker)
            case 'T':
                return database.set_nikkei(ticker)
