"""Email service for sending notifications to users."""
import logging
import os
from typing import List, Dict, Any, Optional
from resend import Emails
from config import config

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails to users."""
    
    def __init__(self):
        """Initialize email service."""
        self.emails = None
        if config.RESEND_API_KEY:
            try:
                # Set API key in environment for resend package
                os.environ["RESEND_API_KEY"] = config.RESEND_API_KEY
                self.emails = Emails()
                logger.info("Email service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize email service: {e}")
        else:
            logger.warning("RESEND_API_KEY not set - email service disabled")
    
    async def send_welcome_email(self, email: str, notification_frequency: str) -> bool:
        """Send welcome email to newly subscribed user."""
        if not self.emails:
            logger.warning("Email service not configured - skipping welcome email")
            return False
        
        try:
            subject = "Welcome to FastFit Radar! 🎉"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to FastFit Radar</title>
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to FastFit Radar!</h1>
                </div>
                
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px; margin-bottom: 20px;">
                        Hi there! 👋
                    </p>
                    
                    <p style="font-size: 16px; margin-bottom: 20px;">
                        Thanks for subscribing to <strong>FastFit Radar</strong>! We're excited to help you discover fashion that matches your unique style.
                    </p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                        <p style="margin: 0; font-size: 14px; color: #666;">
                            <strong>Your notification frequency:</strong> {notification_frequency.replace('_', ' ').title()}
                        </p>
                    </div>
                    
                    <h2 style="color: #667eea; font-size: 20px; margin-top: 30px; margin-bottom: 15px;">What happens next?</h2>
                    
                    <ul style="font-size: 16px; line-height: 1.8; padding-left: 20px;">
                        <li>We'll monitor fashion brand RSS feeds for new releases</li>
                        <li>Our AI will learn your preferences from your feedback</li>
                        <li>You'll receive personalized product recommendations</li>
                        <li>Click "good" or "bad" on products to improve matches</li>
                    </ul>
                    
                    <p style="font-size: 16px; margin-top: 30px; margin-bottom: 20px;">
                        We're already scanning the latest releases for you. Your first personalized recommendations will arrive soon!
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{config.FRONTEND_URL or 'http://localhost:3000'}" style="display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            View Your Dashboard
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                        You're receiving this because you subscribed to FastFit Radar.<br>
                        <a href="{config.FRONTEND_URL or 'http://localhost:3000'}?unsubscribe={email}" style="color: #667eea;">Unsubscribe</a> | 
                        <a href="{config.FRONTEND_URL or 'http://localhost:3000'}?preferences={email}" style="color: #667eea;">Manage Preferences</a>
                    </p>
                </div>
            </body>
            </html>
            """
            
            params = Emails.SendParams({
                "from": config.EMAIL_FROM,
                "to": [email],
                "subject": subject,
                "html": html_body,
            })
            
            email_response = self.emails.send(params)
            
            # Resend returns an Email object or dict with 'id' on success
            email_id = None
            if isinstance(email_response, dict):
                email_id = email_response.get('id')
            elif hasattr(email_response, 'id'):
                email_id = email_response.id
            
            if email_id:
                logger.info(f"Welcome email sent successfully to {email} (id: {email_id})")
                return True
            else:
                logger.error(f"Failed to send welcome email to {email}: {email_response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome email to {email}: {e}", exc_info=True)
            return False
    
    async def send_product_notification(
        self, 
        email: str, 
        products: List[Dict[str, Any]],
        notification_frequency: str
    ) -> bool:
        """Send personalized product notification email."""
        if not self.emails:
            logger.warning("Email service not configured - skipping notification email")
            return False
        
        if not products:
            logger.info(f"No products to send to {email}")
            return False
        
        try:
            subject = f"New releases matching your style ({len(products)} items)"
            
            # Build product cards HTML
            product_cards_html = ""
            for product in products[:10]:  # Limit to top 10
                product_id = product.get("id", "")
                name = product.get("name", "Unknown Product")
                brand = product.get("brand", "Unknown Brand")
                description = product.get("description", "")[:150] + "..." if len(product.get("description", "")) > 150 else product.get("description", "")
                image_url = product.get("image_url", "")
                product_url = product.get("product_url", "#")
                similarity_score = product.get("similarity_score", 0)
                
                # Feedback URLs - point to backend API which will record feedback and redirect
                backend_url = config.BACKEND_URL or "http://localhost:8000"
                good_url = f"{backend_url}/api/user/{email}/feedback/click?product_id={product_id}&feedback=good"
                bad_url = f"{backend_url}/api/user/{email}/feedback/click?product_id={product_id}&feedback=bad"
                
                product_cards_html += f"""
                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                    <div style="display: flex; gap: 20px;">
                        {f'<img src="{image_url}" alt="{name}" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">' if image_url else ''}
                        <div style="flex: 1;">
                            <h3 style="margin: 0 0 10px 0; color: #333; font-size: 18px;">{name}</h3>
                            <p style="margin: 0 0 10px 0; color: #667eea; font-weight: bold; font-size: 14px;">{brand}</p>
                            <p style="margin: 0 0 15px 0; color: #666; font-size: 14px; line-height: 1.5;">{description}</p>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <a href="{product_url}" target="_blank" style="background: #667eea; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; font-size: 14px;">View Product</a>
                                <a href="{good_url}" style="background: #10b981; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; font-size: 14px;">👍 Good</a>
                                <a href="{bad_url}" style="background: #ef4444; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; font-size: 14px;">👎 Bad</a>
                            </div>
                            <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">Match score: {(similarity_score * 100):.0f}%</p>
                        </div>
                    </div>
                </div>
                """
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>New Releases Matching Your Style</title>
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">New Releases Matching Your Style</h1>
                </div>
                
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px; margin-bottom: 20px;">
                        Hi! We found <strong>{len(products)}</strong> new releases that match your taste profile. Check them out below!
                    </p>
                    
                    {product_cards_html}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{config.FRONTEND_URL or 'http://localhost:3000'}" style="display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            View More Products
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                        Your notification frequency: <strong>{notification_frequency.replace('_', ' ').title()}</strong><br>
                        <a href="{config.FRONTEND_URL or 'http://localhost:3000'}?unsubscribe={email}" style="color: #667eea;">Unsubscribe</a> | 
                        <a href="{config.FRONTEND_URL or 'http://localhost:3000'}?preferences={email}" style="color: #667eea;">Manage Preferences</a>
                    </p>
                </div>
            </body>
            </html>
            """
            
            params = Emails.SendParams({
                "from": config.EMAIL_FROM,
                "to": [email],
                "subject": subject,
                "html": html_body,
            })
            
            email_response = self.emails.send(params)
            
            # Resend returns an Email object or dict with 'id' on success
            email_id = None
            if isinstance(email_response, dict):
                email_id = email_response.get('id')
            elif hasattr(email_response, 'id'):
                email_id = email_response.id
            
            if email_id:
                logger.info(f"Product notification email sent successfully to {email} ({len(products)} products) (id: {email_id})")
                return True
            else:
                logger.error(f"Failed to send notification email to {email}: {email_response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending product notification to {email}: {e}", exc_info=True)
            return False

# Global email service instance
email_service = EmailService()

