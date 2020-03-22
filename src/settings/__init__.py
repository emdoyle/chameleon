from environs import Env

env = Env()
env.read_env()

DB_HOST = env("DB_HOST", "localhost")
DB_PORT = env("DB_PORT", 5432)
DB_USER = env("DB_USER", "cham")
DB_NAME = env("DB_NAME", "chameleon")
DB_PASSWORD = env("DB_PASSWORD", "")

COOKIE_SECRET = env("COOKIE_SECRET", "")
