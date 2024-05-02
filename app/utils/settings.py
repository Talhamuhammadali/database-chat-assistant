from decouple import config
# Postgres Config
POSTGRES_HOST = config('POSTGRES_HOST')
POSTGRES_PORT = config('POSTGRES_PORT', default=5432, cast=int)
POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
POSTGRES_DATABASE = config('POSTGRES_DATABASE')