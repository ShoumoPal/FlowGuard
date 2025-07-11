import httpx
import json
import time
from app.logger import rate_logger
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            await asyncio.sleep(index * 0.05)
            start_time = time.perf_counter()
            #print(f"Sending request to : {API_KEY} : {URL}")
            response = await client.get(URL, headers={'X-API-Key': API_KEY})
            latency = (time.perf_counter() - start_time) * 1000
            results.append((response.status_code, latency))
            rate_logger.info(f'response for {API_KEY} : {URL} : {response.status_code}')
    except Exception as e:
        rate_logger.info(f'Timeout error for {API_KEY} on {URL}')
    
async def run_load_test():
    tasks = [send_requests(i) for i in range(TRIES)]
    await asyncio.gather(*tasks)
    report()

def report():
    latencies = [latency for _, latency in results]
    avg_latency = sum(latencies) / len(latencies) if len(latencies) > 0 else 0
    successful_attempts = len([code for code, _ in results if code == 200])
    limited_attempts = len(results) - successful_attempts
    status_codes = Counter([code for code, _ in results])
    rate_logger.info(f'\nTotal attempts: {len(results)}\nSuccessful attempts: {successful_attempts}\nRate limited attempts: {limited_attempts}\nAverage latency of the recent test : {avg_latency}')
    rate_logger.info('Status code summary:')
    for code, count in status_codes.items():
        rate_logger.info(f'{code}:{count}')

if __name__ == '__main__':
    asyncio.run(run_load_test())
    