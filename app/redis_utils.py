import os
from redis import Redis
from fastapi import HTTPException
from .logger import logger

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = Redis.from_url(redis_url, decode_responses=True)

def check_rate_limit(api_key : str, limit : int = 60):
    key = f'ratelimit:{api_key}'
    current = r.get(key)

    if current and int(current) >= limit:
        #logger.info(f'Rate limit exceeded for API key : {api_key}')
        r.incr(f'ratelimit:{api_key}:count', amount=1) # Incrementing total rate limited count for specific API key
        raise HTTPException(status_code=429, detail='Rate limit exceeded')

    pipe = r.pipeline()
    pipe.incr(key, amount=1)
    pipe.expire(key, 60)
    pipe.execute()
