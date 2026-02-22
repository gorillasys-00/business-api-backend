from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import requests
from typing import Dict

router = APIRouter(
    prefix="/api/v1/webhook",
    tags=["webhook"],
)

# In-memory storage for webhook subscriptions
webhook_subscriptions: Dict[str, dict] = {}

class WebhookRegistration(BaseModel):
    target_url: str
    callback_url: str
    event_type: str

@router.post("/register")
async def register_webhook(data: WebhookRegistration):
    """
    Registers a new webhook and returns a subscription_id.
    """
    subscription_id = str(uuid.uuid4())
    webhook_subscriptions[subscription_id] = {
        "target_url": data.target_url,
        "callback_url": data.callback_url,
        "event_type": data.event_type
    }
    return {
        "status": "success",
        "message": "Webhook registered successfully",
        "subscription_id": subscription_id
    }

@router.post("/simulate/{subscription_id}")
async def simulate_webhook(subscription_id: str):
    """
    Simulates sending an event to the registered callback URL.
    """
    if subscription_id not in webhook_subscriptions:
        raise HTTPException(status_code=404, detail="Subscription ID not found")
        
    subscription = webhook_subscriptions[subscription_id]
    
    payload = {
        "event": subscription["event_type"],
        "message": "変化を検知しました",
        "target": subscription["target_url"]
    }
    
    try:
        response = requests.post(subscription["callback_url"], json=payload, timeout=5)
        
        return {
            "status": "success",
            "message": f"Webhook execution simulated successfully.",
            "callback_response_status": response.status_code,
            "callback_response_text": response.text
        }
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to send webhook request to callback_url: {str(e)}"
        )
