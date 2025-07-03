from fastapi import FastAPI, Depends, HTTPException, Request, Query, Header
from .models import SQLModel, APIKey, APIKeyCreate, ResponseLog
from .database import engine, Session, get_session
from .proxy import forward_request
from .redis_utils import check_rate_limit
from contextlib import asynccontextmanager
from sqlmodel import select
import secrets

@asynccontextmanager
async def lifespan(app : FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
async def root():
    return('Crazy')

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

@app.post('/proxy')
async def proxy(request : Request,
                url : str = Query(..., description='URL to proxy to'),
                api_key : str = Header(..., alias='X_API_Key'),
                session : Session = Depends(get_session)):
    key_obj = session.exec(select(APIKey).where(APIKey.key == api_key)).first()
    if not key_obj:
        raise HTTPException(status_code=400, detail='Keys don\'t match')
    
    # Rate limit check
    check_rate_limit(api_key, 2)
    
    # Proxy the request
    result = await forward_request(request=request, destination_url=url)

    log = ResponseLog(
        api_key=api_key,
        latency=result['latency'],
        url=url,
        status_code=result['status_code']
    )

    session.add(log)
    session.commit()
    session.refresh(log)

    return result

# Endpoint for testing data
@app.get('/all_keys')
async def show_all_keys(session : Session = Depends(get_session)):
    return session.exec(select(APIKey)).all()

@app.get('/view_logs')
async def view_all_logs(session : Session = Depends(get_session)):
    return session.exec(select(ResponseLog)).all()