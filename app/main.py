from fastapi import FastAPI, Request, HTTPException, Depends
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

async def check_rate_limit(request: Request):
    api_key = request.headers.get("X-RapidAPI-Key")
    
    # If no premium key is provided, enforce IP limit
    if not api_key or api_key == os.getenv("RAPIDAPI_KEY"):
        # Get real client IP from X-Forwarded-For if behind a proxy like Render
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown-ip"
            
        usage = DEMO_USAGE.get(client_ip, 0)
        
        if usage >= MAX_FREE_CALLS:
            raise HTTPException(
                status_code=429, 
                detail="無料枠（5回）を使い切りました。継続するにはPremiumプランをご検討ください。"
            )
        
        DEMO_USAGE[client_ip] = usage + 1
        return client_ip
    return "premium-bypass"

# Include routers with dependency
app.include_router(esg_score.router, dependencies=[Depends(check_rate_limit)])
app.include_router(niche_data.router, dependencies=[Depends(check_rate_limit)])
app.include_router(web_extract.router, dependencies=[Depends(check_rate_limit)])
app.include_router(text_to_json.router, dependencies=[Depends(check_rate_limit)])
app.include_router(condition_check.router, dependencies=[Depends(check_rate_limit)])
app.include_router(ai_scrape.router, dependencies=[Depends(check_rate_limit)])
app.include_router(format_json.router, dependencies=[Depends(check_rate_limit)])
app.include_router(webhook.router) # Webhook sender is free

@app.get("/")
async def root():
    return {"message": "Welcome to the Business API Backend Foundation. Swagger UI is available at /docs"}
