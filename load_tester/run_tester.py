import httpx
import json
import time
from app.logger import rate_logger
from app.redis_utils import r
import asyncio
from collections import Counter

config = {}
with open(file='load_tester/config.json', mode='r') as f:
    config = json.load(f)

TRIES = config['tries']
API_KEY = config['api_key']
URL = config['proxy_url']

results = []

async def send_requests(index):
    try:
        async with httpx.AsyncClient() as client:
            start_time = time.perf_counter()
            response = await client.post(URL, headers={'X_API_Key': API_KEY})
            latency = (time.perf_counter() - start_time) * 1000
            results.append((response.status_code, latency))
            rate_logger.info(f'response for {API_KEY} : {URL} : {response.status_code}')
    except Exception as e:
        rate_logger.info(f'Error sending request to {URL} with key {API_KEY}')
    
async def run_load_test():
    tasks = [send_requests(i) for i in range(TRIES)]
    await asyncio.gather(*tasks)
    report()

def report():
    latencies = [latency for _, latency in results]
    avg_latency = sum(latencies) / len(latencies) if len(latencies) > 0 else 0
    r_key = f'ratelimit:{API_KEY}:count'
    print(r_key)
    rate_limit_count = r.get(r_key)
    status_codes = Counter([code for code, _ in results])
    rate_logger.info(f'\nTotal attempts: {len(latencies)}\nAverage latency of the recent test : {avg_latency}\nRate limited attempts : {rate_limit_count}')
    rate_logger.info('Status code summary:\n')
    for code, count in status_codes.items():
        rate_logger.info(f'{code}:{count}\n')

    redis_keys = r.keys(f'ratelimit:{API_KEY}*')
    print(f'{redis_keys}')
    for key in redis_keys:
        print(f'{r.get(key)}')
    
    print("[DEBUG] Pinging Redis...")
    try:
        print("[DEBUG] Redis PING:", r.ping())
    except Exception as e:
        print("[DEBUG] Redis connection failed:", e)

if __name__ == '__main__':
    asyncio.run(run_load_test())
    