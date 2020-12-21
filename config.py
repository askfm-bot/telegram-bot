import os


ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']
ADMIN_USERNAME = os.environ['ADMIN_USERNAME']
ALLOWED_USER_IDS = list(map(int, os.environ['ALLOWED_USER_IDS'].split(',')))
APP_NAME = os.environ['APP_NAME']
CHROMEDRIVER_PATH = os.environ['CHROMEDRIVER_PATH']
CONNECTION_STRING = os.environ['CONNECTION_STRING']
GOOGLE_CHROME_PATH = os.environ['GOOGLE_CHROME_BIN']
SECRET = os.environ['SECRET']
TARGET_TELEGRAM_USER_ID = int(os.environ['TARGET_TELEGRAM_USER_ID'])
TOKEN = os.environ['TOKEN']
URL_ASK = 'https://ask.fm/' + os.environ['ASKFM_USERNAME'] + '/ask'
URL_FEED = 'https://ask.fm/' + os.environ['ASKFM_USERNAME']
VK_ACCESS_TOKEN = os.environ['VK_ACCESS_TOKEN']
VK_USER_ID = int(os.environ['VK_USER_ID'])
