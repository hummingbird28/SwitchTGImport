from decouple import config

BOT_TOKEN = config("BOT_TOKEN", default="")
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN", default="")

API_ID = config("API_ID", default=0, cast=int)
API_HASH = config("API_HASH", default="")

DB_KEY = config("DB_KEY", default="change123")

TASK_COUNT = config("TASK_COUNT", default=10, cast=int)

WORKERS = config("WORKERS", cast=int, default=0)