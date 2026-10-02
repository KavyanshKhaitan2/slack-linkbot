import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
