from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.routers import ai_scrape, format_json, esg_score, niche_data, webhook, web_extract, text_to_json, condition_check
import os

app = FastAPI(
    title="Business APIs",
    description="Backend foundation for scalable business APIs",
    version="1.0.0",
)

# In-memory storage for IP-based rate limiting
# { "client_ip": call_count }
DEMO_USAGE = {}
MAX_FREE_CALLS = 5

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only limit AI analysis endpoints
    path = request.url.path
    if path.startswith("/api/v1") and not path.endswith("/webhook"): # Webhook sender itself is free
        # 1. Check for Premium Key (X-RapidAPI-Key)
        # In RapidAPI, the key is passed in this header
        api_key = request.headers.get("X-RapidAPI-Key")
        
        # If no premium key is provided, enforce IP limit
        if not api_key or api_key == os.getenv("RAPIDAPI_KEY"):
            client_ip = request.client.host
            usage = DEMO_USAGE.get(client_ip, 0)
            
            if usage >= MAX_FREE_CALLS:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "無料枠（5回）を使い切りました。継続するにはPremiumプランをご検討ください。"}
                )
            
            # Note: We increment AFTER the response is successful in the routers, 
            # or here if we want to be strict. Let's do it here for simplicity.
            DEMO_USAGE[client_ip] = usage + 1
            
    response = await call_next(request)
    return response

# Include routers
app.include_router(ai_scrape.router)
app.include_router(format_json.router)
app.include_router(esg_score.router)
app.include_router(niche_data.router)
app.include_router(webhook.router)
app.include_router(web_extract.router)
app.include_router(text_to_json.router)
app.include_router(condition_check.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Business API Backend Foundation. Swagger UI is available at /docs"}
