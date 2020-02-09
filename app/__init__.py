"""Initialize application"""

import os
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
import telegram
from telegram.ext import Updater


load_dotenv()

# get logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
TELEGRAM_LOGGER = logging.getLogger('telegram')
TELEGRAM_LOGGER.setLevel(logging.DEBUG)

# create file handler
FILE_HANDLER = logging.FileHandler('output.log')
FILE_HANDLER.setLevel(logging.DEBUG)

# create console handler
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
STREAM_HANDLER.setFormatter(FORMATTER)
FILE_HANDLER.setFormatter(FORMATTER)

# add the handlers to logger
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
TELEGRAM_LOGGER.addHandler(STREAM_HANDLER)
TELEGRAM_LOGGER.addHandler(FILE_HANDLER)

# database
ENGINE = create_engine(os.environ["DATABASE_URI"])
SESSION = sessionmaker(bind=ENGINE)

# scheduler
SCHEDULER = BackgroundScheduler(
    daemon=True,
    job_defaults={'misfire_grace_time': 300},
)
SCHEDULER.start()

TELEGRAM_KEY = os.environ['TELEGRAM_KEY']
# BOT = telegram.Bot(token=TELEGRAM_KEY)
UPDATER = Updater(TELEGRAM_KEY, use_context=True)

# api
BASE_URL = os.environ["API_URL"]
HEADERS = {
    'Authorization': os.environ["API_AUTHORIZATION"]
}
