from fastapi import APIRouter, HTTPException
import trafilatura

router = APIRouter(
    prefix="/api/v1/ai-scrape",
    tags=["ai-scrape"],
)

@router.get("/")
async def get_ai_scrape(url: str):
    """
    Extracts the main content from the provided URL.
    Returns the content in markdown format.
    """
    try:
        # Fetch the web page
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            raise HTTPException(status_code=400, detail="URLが無効、またはアクセスがブロックされました。")
        
        # Extract main content as markdown
        content = trafilatura.extract(downloaded, output_format="markdown")
        
        if content is None:
            raise HTTPException(status_code=500, detail="本文の抽出に失敗しました。")
            
        return {
            "status": "success",
            "url": url,
            "content": content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予期せぬエラーが発生しました: {str(e)}")
