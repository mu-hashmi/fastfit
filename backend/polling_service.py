"""Background polling service for continuous RSS feed polling."""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import logging

from rss_fetcher import rss_fetcher
from agent_memory_client import agent_memory_client
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PollingService:
    """Background service that continuously polls RSS feeds for new products."""
    
    def __init__(self):
        """Initialize polling service."""
        self.is_running = False
        self.last_poll_time = None
        self.processed_product_ids = set()  # Track processed products to avoid duplicates
        
    async def start(self):
        """Start the polling service."""
        if self.is_running:
            logger.warning("Polling service is already running")
            return
        
        self.is_running = True
        logger.info("Starting RSS polling service...")
        logger.info(f"Polling interval: {config.RSS_POLLING_INTERVAL_SECONDS}s")
        
        # Run initial poll immediately
        asyncio.create_task(self._poll_loop())
    
    async def stop(self):
        """Stop the polling service."""
        self.is_running = False
        logger.info("Stopping polling service...")
    
    async def _poll_loop(self):
        """Main polling loop for fetching and storing products from RSS feeds."""
        while self.is_running:
            try:
                logger.info("Fetching products from RSS feeds...")
                products = rss_fetcher.fetch_all_feeds()
                
                # Filter out already processed products
                new_products = [p for p in products if p.get("id") not in self.processed_product_ids]
                
                if new_products:
                    logger.info(f"Found {len(new_products)} new products out of {len(products)} total")
                    
                    # Store products in Redis Memory
                    stored_count = await agent_memory_client.store_products_batch(new_products)
                    logger.info(f"Stored {stored_count} products in Redis Memory")
                    
                    # Track processed products
                    for product in new_products:
                        self.processed_product_ids.add(product.get("id"))
                else:
                    logger.info("No new products found")
                
                self.last_poll_time = datetime.now()
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)
            
            # Wait for next polling interval
            await asyncio.sleep(config.RSS_POLLING_INTERVAL_SECONDS)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current polling service status."""
        return {
            "is_running": self.is_running,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "processed_products_count": len(self.processed_product_ids),
            "polling_interval_seconds": config.RSS_POLLING_INTERVAL_SECONDS
        }

# Global polling service instance
polling_service = PollingService()
