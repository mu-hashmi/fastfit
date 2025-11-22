"""FastAPI main application for FastFit Radar."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
from contextlib import asynccontextmanager
from config import config

logger = logging.getLogger(__name__)

from rss_fetcher import rss_fetcher
from agent_memory_client import agent_memory_client
from polling_service import polling_service
from user_preferences import user_preferences
from email_service import email_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup: Start polling service
    await polling_service.start()
    yield
    # Shutdown: Stop polling service
    await polling_service.stop()
    await agent_memory_client.close()

app = FastAPI(title="FastFit Radar API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SubscribeRequest(BaseModel):
    email: str
    notification_frequency: str = "weekly"  # daily, weekly, realtime

class FeedbackRequest(BaseModel):
    product_id: str
    feedback: str  # "good" or "bad"

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "FastFit Radar API", "status": "running"}

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/api/polling-status")
async def get_polling_status():
    """Get polling service status."""
    return {
        "success": True,
        "status": polling_service.get_status()
    }

# User Subscription Endpoints
@app.post("/api/subscribe")
async def subscribe(request: SubscribeRequest):
    """Subscribe user with email and notification preferences."""
    try:
        prefs = await user_preferences.get_user_preferences(request.email)
        prefs["notification_frequency"] = request.notification_frequency
        success = await user_preferences.store_user_preferences(request.email, prefs)
        
        # Send welcome email
        if success:
            email_sent = await email_service.send_welcome_email(
                request.email, 
                request.notification_frequency
            )
            if not email_sent:
                logger.warning(f"Failed to send welcome email to {request.email}, but subscription succeeded")
        
        return {
            "success": success,
            "email": request.email,
            "message": "Subscribed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{email}/preferences")
async def get_user_preferences_endpoint(email: str):
    """Get user preferences."""
    try:
        prefs = await user_preferences.get_user_preferences(email)
        return {
            "success": True,
            "preferences": prefs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/user/{email}/preferences")
async def update_user_preferences(email: str, preferences: Dict[str, Any]):
    """Update user preferences."""
    try:
        success = await user_preferences.store_user_preferences(email, preferences)
        return {
            "success": success,
            "message": "Preferences updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user/{email}/feedback")
async def submit_feedback(email: str, request: FeedbackRequest):
    """Record user feedback on a product."""
    try:
        success = await user_preferences.update_preferences_from_feedback(
            email, 
            request.product_id, 
            request.feedback
        )
        return {
            "success": success,
            "message": f"Feedback recorded: {request.feedback}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{email}/feedback/click")
async def submit_feedback_from_email(
    email: str,
    product_id: str = Query(..., description="Product ID"),
    feedback: str = Query(..., description="Feedback: 'good' or 'bad'")
):
    """Record user feedback from email click and redirect to thank you page."""
    try:
        if feedback not in ["good", "bad"]:
            raise HTTPException(status_code=400, detail="Feedback must be 'good' or 'bad'")
        
        success = await user_preferences.update_preferences_from_feedback(
            email, 
            product_id, 
            feedback
        )
        
        if success:
            # Return a simple HTML thank you page
            thank_you_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Thank You!</title>
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 32px;">{'👍' if feedback == 'good' else '👎'}</h1>
                </div>
                <div style="background: #f9f9f9; padding: 40px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #667eea; font-size: 24px; margin-bottom: 20px;">Thank You!</h2>
                    <p style="font-size: 18px; margin-bottom: 30px;">
                        Your feedback has been recorded. We'll use this to improve your future recommendations!
                    </p>
                    <p style="font-size: 14px; color: #666;">
                        You can close this window now.
                    </p>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=thank_you_html)
        else:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
    except Exception as e:
        logger.error(f"Error recording feedback from email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Product Endpoints
@app.post("/api/fetch-rss")
async def fetch_rss():
    """Fetch products from RSS feeds manually."""
    try:
        products = rss_fetcher.fetch_all_feeds()
        return {
            "success": True,
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/store-products")
async def store_products(products: List[Dict[str, Any]]):
    """Store products in Agent Memory Server manually."""
    stored_count = await agent_memory_client.store_products_batch(products)
    return {
        "success": True,
        "stored": stored_count,
        "total": len(products)
    }

@app.get("/api/products")
async def get_products(limit: int = 50):
    """Get latest products."""
    try:
        products = await agent_memory_client.retrieve_recent_products(limit)
        return {
            "success": True,
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{email}/matches")
async def get_user_matches(email: str, limit: int = 10):
    """Get personalized product matches for user."""
    try:
        matches = await agent_memory_client.match_products_to_user(email, limit)
        return {
            "success": True,
            "matches": matches,
            "count": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match-products/{email}")
async def match_products_for_user(email: str, limit: int = 10):
    """Match products for user manually."""
    try:
        matches = await agent_memory_client.match_products_to_user(email, limit)
        return {
            "success": True,
            "matches": matches,
            "count": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
