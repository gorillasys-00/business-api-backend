from fastapi import APIRouter, HTTPException, Query
import requests
from bs4 import BeautifulSoup
import os
import json
import re
from dotenv import load_dotenv
from google import genai
import xml.etree.ElementTree as ET

load_dotenv()

router = APIRouter(
    prefix="/api/v1/niche-data",
    tags=["niche-data"],
)

@router.get("/")
async def get_niche_data(
    query: str = Query(..., description="分析キーワード（例：「Japan Anime」など）")
):
    """
    Fetch the latest news from Google News RSS based on the query,
    and analyze the trend using Gemini AI.
    """
    if not query:
        raise HTTPException(status_code=400, detail="query parameter is required")

    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        articles = []
        try:
            root = ET.fromstring(response.content)
            for i, item in enumerate(root.findall(".//item")):
                if i >= 10:
                    break
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                if title:
                    articles.append({
                        "title": title,
                        "url": link
                    })
        except Exception:
            # fallback
            soup = BeautifulSoup(response.content, "html.parser")
            for item in soup.find_all("item")[:10]:
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                if title:
                    articles.append({
                        "title": title,
                        "url": link
                    })
                    
        if not articles:
            raise HTTPException(status_code=404, detail="No relevant articles could be extracted.")
            
        # Analyze with Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")

        client = genai.Client(api_key=api_key)
        
        articles_text = "\n".join([f"- {a['title']} ({a['url']})" for a in articles])
        
        prompt = f"""
以下のキーワード「{query}」に関連する最新ニュース記事のリストから、現在の市場・競合の最新トレンドを要約・分析して、必ず指定のJSON形式のみで出力してください。

【ニュース記事リスト】
{articles_text}

【出力JSONフォーマット】
{{
    "query": "{query}",
    "summary": "抽出した記事全体から読み取れる最新トレンドの要約（3〜4文程度）",
    "key_trends": [
        "重要なトレンドポイント1",
        "重要なトレンドポイント2",
        "重要なトレンドポイント3"
    ],
    "articles": [
        {{ "title": "記事タイトル", "url": "記事URL" }}
    ]
}}
"""
        gemini_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        result_text = gemini_response.text.strip()
        json_match = re.search(r'(\{.*\}|\[.*\])', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(1)
            
        extracted_data = json.loads(result_text)
        return extracted_data

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse Gemini response as JSON.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
