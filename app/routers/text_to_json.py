from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv

# Use the google-genai library as previously configured
from google import genai

load_dotenv()

router = APIRouter(
    prefix="/api/v1/text-to-json",
    tags=["text-to-json"],
)

class TextToJsonRequest(BaseModel):
    text: str
    format_instruction: str

@router.post("/")
async def convert_text_to_json(request_data: TextToJsonRequest):
    """
    ぐちゃぐちゃなテキストを指定された指示に従ってJSON構造に変換して返却します。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEYが設定されていません。.envファイルに設定してください。"
        )

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""以下のテキストから情報を抽出し、ユーザーの指示（{request_data.format_instruction}）に従って、必ずJSON形式のみで出力してください。見つからない項目はnullにしてください。余計なマークダウン（```json 等）は出力に含めないでください。

【対象テキスト】
{request_data.text}
"""

        gemini_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        result_text = gemini_response.text.strip()
        
        # Ensure markdown blocks are removed if generated
        if result_text.startswith("```json"):
            result_text = result_text[7:].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:].strip()
            
        if result_text.endswith("```"):
            result_text = result_text[:-3].strip()
            
        extracted_data = json.loads(result_text)
        return extracted_data

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, 
            detail=f"GeminiからのレスポンスをJSONとしてパースできませんでした。レスポンス: {gemini_response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini APIエラー: {str(e)}")
