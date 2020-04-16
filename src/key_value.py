import logging
from redis import Redis, exceptions as redis_exceptions
from aioredis import create_redis_pool
from src.settings import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_MAIN_DB_NO,
    LOGGER_NAME
)

logger = logging.getLogger(LOGGER_NAME)

r = Redis(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    db=int(REDIS_MAIN_DB_NO),
    charset='utf-8',
    decode_responses=True,
)


# Singleton for getting asynchronous Redis client
class AIORedisContainer:
    __client = None

    @classmethod
    async def set_client(cls):
        cls.__client = await create_redis_pool(
            address=(REDIS_HOST, int(REDIS_PORT)),
            db=int(REDIS_MAIN_DB_NO)
        )

    @classmethod
    def get_client(cls):
        return cls.__client


try:
    r.ping()
except redis_exceptions.ConnectionError:
    logger.error("Could not connect to Redis!")
    r = None
