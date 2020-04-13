from environs import Env

env = Env()
env.read_env()

DB_HOST = env("DB_HOST", "localhost")
DB_PORT = env("DB_PORT", "5432")
DB_USER = env("DB_USER", "cham")
DB_NAME = env("DB_NAME", "chameleon")
DB_PASSWORD = env("DB_PASSWORD", "")

REDIS_HOST = env("REDIS_HOST", "localhost")
REDIS_PORT = env("REDIS_PORT", "6379")
REDIS_MAIN_DB_NO = env("REDIS_MAIN_DB_NO", "0")

COOKIE_SECRET = env("COOKIE_SECRET", "")

CORS_ORIGINS = [
    'localhost',
    'evandoyle.net'
]
