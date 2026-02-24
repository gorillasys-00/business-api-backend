from fastapi import APIRouter, HTTPException, Query
import requests
from bs4 import BeautifulSoup
import os
import json
import re
from dotenv import load_dotenv

# Use the new google-genai library as previously configured
from google import genai

load_dotenv()

router = APIRouter(
    prefix="/api/v1/web-extract",
    tags=["web-extract"],
)

@router.get("/")
async def get_web_extract(
    url: str = Query(..., description="抽出対象のWebページのURL"),
    target: str = Query(..., description="抽出したい情報（例：「会社名と代表者名」「料金プラン」など）")
):
    """
    指定されたURLのWebページからテキストを抽出し、Gemini APIを用いてユーザーが要求する情報を抽出してJSONで返却します。
    """
    # 1. Fetch HTML using requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400, 
            detail=f"指定されたURLへのアクセスに失敗しました: {str(e)}"
        )
        
    # 2. Extract text using BeautifulSoup
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove unwanted tags
        for script_or_style in soup(["script", "style", "noscript", "meta", "link", "header", "footer"]):
            script_or_style.decompose()
            
        text = soup.get_text(separator="\n")
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        # Truncate to 15000 characters
        truncated_text = text[:15000]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"HTMLからテキストを抽出中にエラーが発生しました: {str(e)}"
        )
        
    # 3. Call Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEYが設定されていません。.envファイルに設定してください。"
        )

    try:
        client = genai.Client(api_key=api_key)
        
        # 4. Prompt instruction
        prompt = f"""
以下のWebページのテキストから、ユーザーの要求（{target}）を満たす情報を抽出し、必ず純粋なJSON形式のみで出力してください。見つからない場合はnullにしてください。マークダウン記法（```jsonなど）や前置きの文章、解説は一切含めないでください。

[Webページテキスト]
{truncated_text}
"""

        gemini_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=genai.types.GenerateContentConfig(temperature=0.0),
        )
        
        # 5. Parse JSON
        result_text = gemini_response.text.strip()
        
        # 確実なJSON抽出処理 (前後の余分なテキストを削る)
        json_match = re.search(r'(\{.*\}|\[.*\])', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(1)
            
        extracted_data = json.loads(result_text)
        return extracted_data

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, 
            detail=f"GeminiからのレスポンスをJSONとしてパースできませんでした。レスポンス: {gemini_response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini APIエラー: {str(e)}")
