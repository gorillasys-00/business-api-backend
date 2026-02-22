from fastapi import FastAPI
from app.routers import ai_scrape, format_json, esg_score, niche_data, webhook, web_extract, text_to_json

app = FastAPI(
    title="Business APIs",
    description="Backend foundation for scalable business APIs",
    version="1.0.0",
)

# Include routers
app.include_router(ai_scrape.router)
app.include_router(format_json.router)
app.include_router(esg_score.router)
app.include_router(niche_data.router)
app.include_router(webhook.router)
app.include_router(web_extract.router)
app.include_router(text_to_json.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Business API Backend Foundation. Swagger UI is available at /docs"}
