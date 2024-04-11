from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
import yfinance as yf
import plotly.graph_objs as go
import talib
import os
from dotenv import load_dotenv
from src.log import logger
from src import selection
import requests


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    load_dotenv()
    if str(chat_id) != os.environ.get('CHAT_ID'):
        return None
    logger.info(f"ChatID: {chat_id} - chart")
    ticker = update.message.text.replace('/chart', '').strip()
    if ticker == "":
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please enter the ticker.\ne.g.) /chart AAPL"
        )
    else:
        await process_chart(chat_id, context, ticker)


async def process_chart(chat_id, context: ContextTypes.DEFAULT_TYPE, ticker):
    ticker = ticker.upper()
    data = selection.select_data(yf.Ticker(ticker).history(period='100d', interval='1d'))
    curr = data.index[-1].strftime("%Y-%m-%d")

    # Bollinger Bands Chart
    fig_bb = go.Figure()

    # Calculate the 20-period Simple Moving Average (SMA)
    data['SMA'] = data['Close'].rolling(window=14).mean()
    # Calculate the 20-period Standard Deviation (SD)
    data['SD'] = data['Close'].rolling(window=14).std()
    # Calculate the Upper Bollinger Band (UB) and Lower Bollinger Band (LB)
    data['UB'] = data['SMA'] + 2 * data['SD']
    data['LB'] = data['SMA'] - 2 * data['SD']

    # Add the Bollinger Bands to the chart
    fig_bb.add_trace(go.Scatter(x=data.index, y=data['UB'], mode='lines', name='Upper BB', line=dict(color='red')))
    fig_bb.add_trace(go.Scatter(x=data.index, y=data['LB'], fill='tonexty', name='BB', line=dict(color='yellow')))
    fig_bb.add_trace(go.Scatter(x=data.index, y=data['LB'], mode='lines', name='Lower BB', line=dict(color='blue')))
    fig_bb.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='Middle BB', line=dict(color='green')))
    fig_bb.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Price', line=dict(color='black')))
    fig_bb.update_layout(title=f'{ticker} Stock Price with Bollinger Bands', xaxis_title='Date', yaxis_title='Price',
                         showlegend=True)

    # ADX Chart
    fig_adx = go.Figure()
    adx = talib.ADX(data['High'], data['Low'], data['Close'], timeperiod=14)

    # Add the ADX
    fig_adx.add_trace(go.Scatter(x=data.index, y=[40 for _ in range(len(data.index))], mode='lines', name='Strong',
                                 line=dict(color='red')))
    fig_adx.add_trace(go.Scatter(x=data.index, y=adx, mode='lines', name='ADX', line=dict(color='purple')))
    fig_adx.add_trace(go.Scatter(x=data.index, y=[20 for _ in range(len(data.index))], mode='lines', name='Weak',
                                 line=dict(color='blue')))
    fig_adx.update_layout(title=f'{ticker} ADX', xaxis_title='Date', yaxis_title='ADX', showlegend=True)

    # Volume Chart
    fig_vol = go.Figure()

    # Add the Volume
    fig_vol.add_trace(go.Scatter(x=data.index, y=data['Volume'], mode='lines', name='Volume', line=dict(color='black')))
    fig_vol.update_layout(title=f'{ticker} Volume', xaxis_title='Date', yaxis_title='Volume', showlegend=True)

    logger.info(f"{curr}: {ticker} Chart")
    # Convert to png
    fig_bb.write_image(f"./charts/{curr}:{ticker}:Chart.png", format="png", engine="kaleido", width=1920,
                       height=1080)
    fig_adx.write_image(f"./charts/{curr}:{ticker}:ADX.png", format="png", engine="kaleido", width=1920,
                        height=1080)
    fig_vol.write_image(f"./charts/{curr}:{ticker}:Volume.png", format="png", engine="kaleido", width=1920,
                        height=1080)
    # Send to telegram
    url = f"{os.environ.get('NOW_URL')}{ticker}?{os.environ.get('PARAMS')}"
    headers = {
        "User-Agent": os.environ.get('USER_AGENT'),
        "Cookie": os.environ.get('NOW_COOKIE')}
    info = requests.get(url, headers=headers).json()['quoteSummary']['result'][0]['quoteType']['longName']

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"{curr}\n"
             f"{info} ({ticker})"
    )
    await context.bot.send_media_group(
        chat_id=chat_id,
        media=[InputMediaPhoto(open(f"./charts/{curr}:{ticker}:Chart.png", 'rb'), caption=f"{curr}: {ticker} Chart\n"),
               InputMediaPhoto(open(f"./charts/{curr}:{ticker}:ADX.png", 'rb'), caption=f"{curr}: {ticker} ADX\n"),
               InputMediaPhoto(open(f"./charts/{curr}:{ticker}:Volume.png", 'rb'),
                               caption=f"{curr}: {ticker} Volume\n")],
    )
    # Remove png
    os.remove(f"./charts/{curr}:{ticker}:Chart.png")
    os.remove(f"./charts/{curr}:{ticker}:ADX.png")
    os.remove(f"./charts/{curr}:{ticker}:Volume.png")
