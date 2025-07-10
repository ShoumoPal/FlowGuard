from fastapi import FastAPI, Depends, HTTPException, Request, Query, Header
from .models import SQLModel, APIKey, APIKeyCreate, ResponseLog, Metrics
from .database import engine, Session, get_session
from .proxy import forward_request
from .redis_utils import check_rate_limit, r
from contextlib import asynccontextmanager
from sqlmodel import select
import secrets
from .load_balancer import LoadBalancer, Backend
import asyncio

@asynccontextmanager
async def lifespan(app : FastAPI):
    SQLModel.metadata.create_all(engine)

    backends = [
        {'url':'http://host.docker.internal:8001', 'health':'Healthy', 'server_id':'server_1'},
        {'url':'http://host.docker.internal:8002', 'health':'Healthy', 'server_id':'server_2'},
        {'url':'http://host.docker.internal:8003', 'health':'Healthy', 'server_id':'server_3'}
    ]

    balancer_instance = LoadBalancer()
    balancer_instance.configure_load_balancer(backend_list=backends)

    app.state.balancer = balancer_instance

    task = asyncio.create_task(balancer_instance.periodic_health_check(10.0))

    yield

    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get('/')
async def root():
    return('Welcome to my project')

@app.post('/register')
async def register_key(payload : APIKeyCreate, session : Session = Depends(get_session)):
    # Check for existing key
    existing_key = session.exec(select(APIKey).where(payload.owner == APIKey.owner)).first()
    if existing_key:
        raise HTTPException(status_code=400, detail='API key already exists...')

    key = secrets.token_hex(16) # 32-char secure key
    api_key = APIKey(owner=payload.owner, key=key)
    session.add(api_key)
    session.commit()
    session.refresh(api_key)
    return {
        'api_key' : api_key.key,
        'owner' : api_key.owner
    }

@app.get('/proxy')
async def proxy(request : Request,
                #url : str = Query(..., description='URL to proxy to'),
                api_key : str = Header(..., alias='X-API-Key'),
                session : Session = Depends(get_session)):
    key_obj = session.exec(select(APIKey).where(APIKey.key == api_key)).first()
    if not key_obj:
        raise HTTPException(status_code=400, detail='Keys don\'t match')
    
    # Rate limit check
    check_rate_limit(api_key, 2)
    
    backend : Backend = await request.app.state.balancer.get_server()

    # Proxy the request
    result = await forward_request(request=request, destination_url=backend.url)

    log = ResponseLog(
        api_key=api_key,
        latency=result['latency'],
        url=backend.url,
        status_code=result['status_code']
    )

    session.add(log)
    session.commit()
    session.refresh(log)

    return result

@app.get('/metrics/{api_key}')
async def get_metrics(api_key : str, session : Session = Depends(get_session)):
    logs = session.exec(select(ResponseLog).where(ResponseLog.api_key == api_key)).all()

    if not logs:
        raise HTTPException(status_code=400 ,detail='No logs available for this API_Key')

    total_req = len(logs)
    avg_latency = sum(l.latency for l in logs) / total_req
    redis_key = f'ratelimit:{api_key}:count'
    rate_limit_count = int(r.get(redis_key) or 0)
    codes = [l.status_code for l in logs]

    return Metrics(
        total_requests=total_req,
        avg_latency=avg_latency,
        recent_rate_limited_request_count=rate_limit_count,
        recent_codes=codes
    )

# Endpoint for testing data
@app.get('/all_keys')
async def show_all_keys(session : Session = Depends(get_session)):
    return session.exec(select(APIKey)).all()

@app.get('/view_logs')
async def view_all_logs(session : Session = Depends(get_session)):
    return session.exec(select(ResponseLog)).all()

@app.get('/server')
async def get_backend(request : Request):
    backend = await request.app.state.balancer.get_server()
    return {'Server returned':backend.server_id,
            'URL':backend.url}

