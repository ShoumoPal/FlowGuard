import os
from redis import Redis
from fastapi import HTTPException

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = Redis.from_url(redis_url)

def check_rate_limit(api_key : str, limit : int = 2):
    key = f'ratelimit:{api_key}'
    current = r.get(key)

    if current and int(current) >= limit:
        raise HTTPException(status_code=439, detail='Rate limit exceeded')

    pipe = r.pipeline()
    pipe.incr(key, amount=1)
    pipe.expire(key, 60)
    pipe.execute()
