import httpx
import time
from dataclasses import dataclass
from typing import List
from .logger import load_logger
import asyncio

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
    
    def configure_load_balancer(self, backend_list : List[dict]):
        for backend in backend_list:
            self.backends.append(Backend(url=backend['url'], health=backend['health'], server_id=backend['server_id'], response_time=0.0, failure_count=0))
    
    async def health_check(self, backend : Backend):
        try:
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                reponse = await client.get(backend.url)
                end_time = time.time()

                backend.response_time = (end_time - start_time) * 1000

                if reponse.status_code == 200:
                    backend.health = 'Healthy'
                else:
                    backend.health = 'Unhealthy'
        except Exception as e:
            load_logger.info(f'Error while performing health check on {backend.server_id} running on {backend.url}')
    
    async def periodic_health_check(self, interval : float):
        while True:
            try:
                for backend in self.backends:
                    await self.health_check(backend)
                    asyncio.sleep(interval)
            except Exception as e:
                load_logger.debug('Error in periodic health check function...')

    async def get_server(self):
        '''Getting a backend server using Round-Robin method'''
        backends = self.get_healthy_servers()
        #TODO
    
    def get_healthy_servers(self):
        return [backend for backend in self.backends if backend.health == 'Healthy']
                
