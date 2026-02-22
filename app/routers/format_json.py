from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

router = APIRouter(
    prefix="/api/v1/format-json",
    tags=["format-json"],
)

class FormattingRequest(BaseModel):
    text: str
    schema_instruction: str

@router.post("/")
async def post_format_json(payload: FormattingRequest):
    """
    Uses Gemini API to format raw text into structured JSON 
    based on the provided schema instruction.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEYが設定されていません。.envファイルに設定してください。"
        )

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        以下のテキストを分析し、指示されたスキーマ（JSON構造）に従ってJSONフォーマットで出力してください。
        必ず有効なJSONテキストのみを出力し、Markdownブロック（```json など）は含めないでください。

        [テキスト]
        {payload.text}

        [スキーマ（出力形式の指示）]
        {payload.schema_instruction}
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # パースして有効なJSONか確認
        try:
            # Markdownブロック（```json ... ```）が含まれていた場合は除去する
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            structured_json = json.loads(result_text.strip())
            return {"status": "success", "data": structured_json}
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500, 
                detail=f"GeminiからのレスポンスをJSONとしてパースできませんでした。レスポンス: {response.text}"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini APIエラー: {str(e)}")
