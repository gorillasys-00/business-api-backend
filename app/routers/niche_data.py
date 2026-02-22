from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup

router = APIRouter(
    prefix="/api/v1/niche-data",
    tags=["niche-data"],
)

@router.get("/")
async def get_niche_data():
    """
    Fetch the latest IT news from Yahoo News.
    """
    url = "https://news.yahoo.co.jp/topics/it"
    try:
        # User-Agent is often required to avoid being blocked by simple scrapers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        articles = []
        
        # In Yahoo News Topics, headlines are usually found in anchor tags inside specific classes
        # Due to dynamic classes, we'll look for links pointing to particular article/pickup pages
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            title = a_tag.get_text(strip=True)
            
            # Simple heuristic to identify news articles
            if href.startswith("https://news.yahoo.co.jp/pickup/") or href.startswith("https://news.yahoo.co.jp/articles/"):
                if title and not any(article["url"] == href for article in articles):
                    articles.append({
                        "title": title,
                        "url": href
                    })
            if len(articles) >= 10:
                break
                
        return {
            "status": "success",
            "source": "Yahoo News",
            "data": articles
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
