import logging

import redis
import redis.asyncio as redis
from auth.core.settings import settings
from auth.core.config import setup_logging
from datetime import timedelta

setup_logging()

REDIS_URL = settings.redis.redis_url
TOKEN_EXPIRATION_TIME = settings.jwt.access_token_expire_minutes


async def get_redis() -> redis:
    return await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def add_token_to_blacklist(token: str, redis_client, expiration: int = TOKEN_EXPIRATION_TIME) -> None:
    await redis_client.setex(token, timedelta(minutes=expiration), "blacklisted")
    logging.info("Token marked as blacklisted")


async def is_token_blacklisted(token: str, redis_client) -> bool:
    return await redis_client.get(token) == "blacklisted"


async def remove_token_from_blacklist(token: str, redis_client) -> None:
    await redis_client.delete(token)
    logging.info("Token removed from blacklist")
