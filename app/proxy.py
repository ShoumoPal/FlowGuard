import httpx
import time
from fastapi import Request, HTTPException

async def forward_request(request : Request, destination_url : str):
    try:
        async with httpx.AsyncClient() as client:
            body = await request.body()
            headers = request.headers
            method = request.method

            start = time.monotonic()
            response = await client.request(
                method=method,
                url=destination_url,
                headers=headers,
                content=body,
                timeout=3.0
            )
            end = time.monotonic()

            latency = (end-start)*1000

            return {
                'status_code':response.status_code,
                'content':response.text,
                'latency':latency,
                'headers':response.headers
            }
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=str(e))