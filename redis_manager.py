import redis.asyncio as redis
from config import REDIS_URL

redis_client = None

async def init_redis():
    global redis_client
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)