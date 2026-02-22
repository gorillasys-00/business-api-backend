from fastapi import APIRouter, HTTPException
import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

router = APIRouter(
    prefix="/api/v1/esg-score",
    tags=["esg-score"],
)

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

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"企業『{company_name}』の一般的なESG（環境・社会・ガバナンス）の取り組みについて評価し、JSON形式で出力してください。出力するJSONのキーは company_name (文字列), esg_score (1〜100の推定スコア数値), summary (100字程度の要約), key_initiatives (主な取り組み3つの配列) としてください。"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # パースして有効なJSONか確認
        try:
            # Markdownブロック（```json ... ```）が含まれていた場合は除去する
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:].strip()
                
            if result_text.endswith("```"):
                result_text = result_text[:-3].strip()
            
            structured_json = json.loads(result_text)
            return structured_json
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500, 
                detail=f"GeminiからのレスポンスをJSONとしてパースできませんでした。レスポンス: {response.text}"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini APIエラー: {str(e)}")
