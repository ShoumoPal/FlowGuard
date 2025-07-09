from fastapi import FastAPI, HTTPException
import uvicorn
import random
import sys

def start_server(server_id : str, port : int):
    app = FastAPI()

    @app.get('/')
    async def root():
        return {'message':f'Welcome to backend on port {port} with id {server_id}'}
    
    @app.get('/health')
    async def health():
        if random.random() < 0.1:
            raise HTTPException(status_code=500, detail=f'Server {server_id} is currently unhealthy...')
        else:
            return {'status':'Healthy'}, 200
    
    return app

if __name__ == '__main__':
    port = int(sys.argv[1])
    server_id = sys.argv[2]

    uvicorn.run(start_server(server_id, port), port=port, host='0.0.0.0')