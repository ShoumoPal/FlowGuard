import httpx
import time
from dataclasses import dataclass
from typing import List
from .logger import load_logger
import asyncio
from fastapi import HTTPException

@dataclass
class Backend:
    url : str
    health : str
    server_id : str
    response_time : float
    failure_count : int

class LoadBalancer:
    def __init__(self):
        self.backends : List[Backend] = []
        self.index : int = 0
        self.lock = asyncio.Lock()

    def configure_load_balancer(self, backend_list : List[dict]):
        for backend in backend_list:
            self.backends.append(Backend(url=backend['url'], health=backend['health'], server_id=backend['server_id'], response_time=0.0, failure_count=0))
    
    async def health_check(self, backend : Backend):
        try:
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                response = await client.get(backend.url + '/health', timeout=5.0)
                end_time = time.time()

                backend.response_time = (end_time - start_time) * 1000

                if response.status_code == 200:
                    backend.health = 'Healthy'
                else:
                    backend.health = 'Unhealthy'
                    backend.failure_count += 1
                    load_logger.info(f'Backend {backend.server_id} set to status {backend.health}')
        except Exception as e:
            load_logger.error(f'Error while performing health check on {backend.server_id} running on {backend.url}')
            load_logger.error(f'Reason : {str(e)}')
    
    async def periodic_health_check(self, interval : float):
        while True:
            try:
                for backend in self.backends:
                    await self.health_check(backend)
                    await asyncio.sleep(interval)
            except Exception as e:
                load_logger.error('Error in periodic health check function...')

    async def get_server(self):
        '''Getting a backend server using Round-Robin method'''
        backends = self.get_healthy_servers()
        if not backends:
            raise HTTPException(status_code=502, detail='No healthy backends available')
        async with self.lock:
            backend = backends[self.index]
            self.index = (self.index + 1) % len(backends)
        load_logger.info(f"Returned backend : {backend.server_id}")
        return backend
    
    def get_healthy_servers(self):
        return [backend for backend in self.backends if backend.health == 'Healthy']
    
    def get_server_stats(self):
        res = []
        for i, backend in enumerate(self.backends):
            res.append({
                'id' : i + 1,
                'URL' : backend.url,
                'Server ID' : backend.server_id,
                'Response time' : backend.response_time,
                'Failure count' : backend.failure_count
            })
        return res
                
