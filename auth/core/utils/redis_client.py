import logging

import redis
from redis import Redis
from auth.core.settings import settings
from auth.core.config import setup_logging

setup_logging()

REDIS_URL = settings.redis.redis_url
TOKEN_EXPIRATION_TIME = settings.jwt.access_token_expire_minutes

async def get_redis():
    return redis.from_url(REDIS_URL, decode_response=True)


async def add_token_to_blacklist(token: str, redis_client, expiration: int = TOKEN_EXPIRATION_TIME):
    await redis_client.setex(token, timedelta(seconds=expiration), "blacklisted")
    logging.info("Token marked as blacklisted")


async def is_token_blacklisted(token: str, redis_client) -> bool:
    return await redis_client.get(token) == "blacklisted"