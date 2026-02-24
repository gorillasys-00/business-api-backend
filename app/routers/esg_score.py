from fastapi import APIRouter, HTTPException
import os
import json
import re
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List

load_dotenv()

router = APIRouter(
    prefix="/api/v1/esg-score",
    tags=["esg-score"],
)

# In-memory cache for ESG scores
# Key: company_name, Value: structured JSON response
ESG_CACHE = {}

class ESGScoreResponse(BaseModel):
    company_name: str
    esg_score: int
    environmental_score: int
    social_score: int
    governance_score: int
    summary: str
    key_initiatives: List[str]

@router.get("/")
async def get_esg_score(company_name: str):
    """
    ESG・サステナビリティ簡易スコアリング機能
    Takes a company_name parameter.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEYが設定されていません。.envファイルに設定してください。"
        )

    # Check cache first
    if company_name in ESG_CACHE:
        return ESG_CACHE[company_name]

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"企業『{company_name}』の一般的なESG（環境・社会・ガバナンス）の取り組みについて評価し、必ず指定されたJSON構造で出力してください。\n出力するJSONのキーは company_name (文字列), esg_score (1〜100の推定総合スコア数値), environmental_score (1〜100の推定Eスコア数値), social_score (1〜100の推定Sスコア数値), governance_score (1〜100の推定Gスコア数値), summary (100字程度の要約), key_initiatives (主な取り組み3つの配列) としてください。"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.0, 
                seed=42,
                response_mime_type="application/json",
                response_schema=ESGScoreResponse,
            ),
        )
        
        # パースして有効なJSONか確認
        try:
            result_text = response.text.strip()
            
            # 確実なJSON抽出処理 (前後の余分なテキストを削る)
            import re
            json_match = re.search(r'(\{.*\}|\[.*\])', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            
            structured_json = json.loads(result_text)
            
            # Save to cache
            ESG_CACHE[company_name] = structured_json
            
            return structured_json
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500, 
                detail=f"GeminiからのレスポンスをJSONとしてパースできませんでした。レスポンス: {response.text}"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini APIエラー: {str(e)}")
