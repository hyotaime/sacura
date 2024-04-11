from telegram import Update
from telegram.ext import ContextTypes
from src.log import logger
import os
from dotenv import load_dotenv
import datetime
import requests
from pytz import timezone


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    load_dotenv()
    if str(chat_id) != os.environ.get('CHAT_ID'):
        return None
    logger.info(f"ChatID: {chat_id} - now")
    # 입력 메시지에서 '/now'를 제외한 텍스트 추출
    ticker = update.message.text.replace('/now', '').strip()
    if ticker == "":
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please enter the ticker.\ne.g.) /now AAPL"
        )
    else:
        await process_now_value(chat_id, context, ticker)


async def n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    load_dotenv()
    if str(chat_id) != os.environ.get('CHAT_ID'):
        return None
    logger.info(f"ChatID: {chat_id} - n")
    # 입력 메시지에서 '/n'를 제외한 텍스트 추출
    ticker = update.message.text.replace('/n', '').strip()
    if ticker == "":
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please enter the ticker.\ne.g.) /n AAPL"
        )
    else:
        await process_now_value(chat_id, context, ticker)


async def process_now_value(chat_id: int, context: ContextTypes.DEFAULT_TYPE, ticker: str):
    ticker = ticker.upper().strip()
    try:
        response = now_crawling(ticker)
        if response is not None:
            response = response[0]
            name = response['quoteType']['longName']
            symbol = response['quoteType']['symbol']
            tz = response['quoteType']['timeZoneFullName']
            time = datetime.datetime.now(timezone(tz)).strftime("%Y-%m-%d %H:%M:%S")
            detail = response['summaryDetail']
            try:
                current_price = response['financialData']['currentPrice']['fmt']
            except Exception:
                current_price = f"{(detail['ask']['raw'] + detail['bid']['raw']) / 2 :.2f}"
            currency = detail['currency']
            open_price = detail['open']['fmt']
            high_price = detail['dayHigh']['fmt']
            low_price = detail['dayLow']['fmt']
            previous_close_price = detail['previousClose']['fmt']
            volume = detail['volume']['fmt']
            if currency == 'KRW':
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{time} {currency}\n"
                         f"{name} ({symbol})\n"
                         f"Current Price: {current_price.replace('.00', '')}\n"
                         f"Open: {open_price.replace('.00', '')}\n"
                         f"High: {high_price.replace('.00', '')}\n"
                         f"Low: {low_price.replace('.00', '')}\n"
                         f"Previous Close: {previous_close_price.replace('.00', '')}\n"
                         f"Volume: {volume}\n"
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{time} {currency}\n"
                         f"{name} ({symbol})\n"
                         f"Current Price: {current_price}\n"
                         f"Open: {open_price}\n"
                         f"High: {high_price}\n"
                         f"Low: {low_price}\n"
                         f"Previous Close: {previous_close_price}\n"
                         f"Volume: {volume}\n"
                )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Can't find any result."
            )
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Can't find any result."
        )


def now_crawling(ticker):
    ticker = ticker.upper()
    load_dotenv()
    USER_AGENT = os.environ.get('USER_AGENT')
    NOW_URL = os.environ.get('NOW_URL')
    PARAMS = os.environ.get('PARAMS')
    NOW_COOKIE = os.environ.get('NOW_COOKIE')
    url = f"{NOW_URL}{ticker}?{PARAMS}"
    headers = {"User-Agent": USER_AGENT, "Cookie": NOW_COOKIE}
    response = requests.get(url, headers=headers).json()['quoteSummary']['result']
    return response
