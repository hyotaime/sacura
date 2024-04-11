import sys
sys.path.append('/sacura')

import telegram as tel
from telegram.ext import CommandHandler, ApplicationBuilder
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src import log, chart_control, database
from commands import start, add, remove, now, chart

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = tel.Bot(token=BOT_TOKEN)

if __name__ == '__main__':
    log.logger.addHandler(log.stream_handler)
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    database.db_connection_test()
    try:
        os.mkdir('./charts')
    except FileExistsError:
        pass
    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(chart_control.night, 'cron', day_of_week='mon-fri', hour=22, minute=0, args=(application, ), id='night')
    scheduler.add_job(chart_control.morning, 'cron', day_of_week='mon-fri', hour=8, minute=30, args=(application, ), id='morning')

    start_handler = CommandHandler('start', start.start)
    application.add_handler(start_handler)

    add_handler = CommandHandler('add', add.add)
    application.add_handler(add_handler)
    a_handler = CommandHandler('a', add.a)
    application.add_handler(a_handler)

    remove_handler = CommandHandler('remove', remove.remove)
    application.add_handler(remove_handler)
    r_handler = CommandHandler('r', remove.r)
    application.add_handler(r_handler)

    now_handler = CommandHandler('now', now.now)
    application.add_handler(now_handler)
    n_handler = CommandHandler('n', now.n)
    application.add_handler(n_handler)

    chart_handler = CommandHandler('chart', chart.chart)
    application.add_handler(chart_handler)

    application.run_polling()
