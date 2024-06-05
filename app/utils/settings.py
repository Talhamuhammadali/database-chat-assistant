from decouple import config
# Postgres Config
POSTGRES_STT_HOST = config('POSTGRES_STT_HOST', default="")
POSTGRES_STT_PORT = config('POSTGRES_STT_PORT', default=5432, cast=int)
POSTGRES_STT_USER = config('POSTGRES_STT_USER')
POSTGRES_STT_PASSWORD = config('POSTGRES_STT_PASSWORD')
POSTGRES_STT_DATABASE = config('POSTGRES_STT_DATABASE')
# LLM Server URLs
SQL_URL = config("SQL_URL")
CHAT_URL = config("CHAT_URL")
# MYSQL configs
MYSQL_USER = config('MYSQL_USER')
MYSQL_PASS = config('MYSQL_PASS')
MYSQL_HOST = config('MYSQL_HOST')
MYSQL_PORT = config('MYSQL_PORT', default=3306)
MYSQL_DB = config('MYSQL_DB')
# Phoenix
PHOENIX_COLLECTOR_ENDPOINT = config('PHOENIX_COLLECTOR_ENDPOINT')
# API keys
GROQ_API_KEY = config('GROQ_API_KEY')