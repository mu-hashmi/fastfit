"""Redis Agent Memory Server client for FastFit Radar."""
from typing import List, Dict, Any, Optional
import httpx
import asyncio
import re
from config import config

class AgentMemoryClient:
    """Client for Redis Agent Memory Server."""
    
    def __init__(self):
        """Initialize Agent Memory Server client."""
        self.base_url = config.AGENT_MEMORY_SERVER_URL
        self.user_id = config.AGENT_MEMORY_USER_ID
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0, connect=10.0),  # 30s total, 10s connect
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def search_memories(
        self, 
        query: str, 
        limit: int = 50,
        user_id_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search memories using semantic search."""
        try:
            # Build search request body
            search_request = {
                "text": query,
                "user_id": {"eq": user_id_filter or self.user_id},
                "limit": min(limit, 100)  # API max is 100
            }
            
            response = await self.client.post(
                "/v1/long-term-memory/search",
                json=search_request
            )
            response.raise_for_status()
            result = response.json()
            return result.get("memories", [])
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    async def store_product_memory(self, product: Dict[str, Any]) -> bool:
        """Store a product as a long-term memory."""
        try:
            product_id = product.get("id", "")
            if not product_id:
                return False
            
            # Build text content from name and description
            text_parts = []
            if product.get("name"):
                text_parts.append(product.get("name"))
            if product.get("description"):
                text_parts.append(product.get("description"))
            text = " ".join(text_parts) or "Product"
            
            memory_data = {
                "id": f"product_{product_id}",
                "text": text,
                "user_id": self.user_id,
                "memory_type": "semantic",
                "topics": [product.get("brand", "unknown")] if product.get("brand") else None,
                "entities": [
                    f"product_id:{product_id}",
                    f"image_url:{product.get('image_url', '')}",
                    f"product_url:{product.get('product_url', '')}",
                    f"brand:{product.get('brand', 'unknown')}"
                ]
            }
            
            response = await self.client.post(
                "/v1/long-term-memory/",
                json={"memories": [memory_data], "deduplicate": True}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error storing product memory {product.get('id', 'unknown')}: {e}")
            return False
    
    async def store_products_batch(self, products: List[Dict[str, Any]]) -> int:
        """Store multiple products as memories in batch."""
        if not products:
            return 0
        
        batch_size = 10
        stored_count = 0
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            results = await asyncio.gather(
                *[self.store_product_memory(product) for product in batch],
                return_exceptions=True
            )
            stored_count += sum(1 for r in results if r is True)
        
        return stored_count
    
    async def retrieve_recent_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent products from memory."""
        try:
            memories = await self.search_memories(
                query="fashion clothing products new releases",
                limit=limit
            )
            
            products = []
            for memory in memories:
                memory_id = memory.get("id", "")
                if not memory_id.startswith("product_"):
                    continue
                
                product_id = memory_id.replace("product_", "")
                entities = memory.get("entities", [])
                
                # Extract product data from entities
                image_url = ""
                product_url = ""
                brand = "unknown"
                
                for entity in entities:
                    if entity.startswith("image_url:"):
                        image_url = entity.split(":", 1)[1]
                    elif entity.startswith("product_url:"):
                        product_url = entity.split(":", 1)[1]
                    elif entity.startswith("brand:"):
                        brand = entity.split(":", 1)[1]
                
                text = memory.get("text", "")
                # Strip HTML if present
                if text:
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
                    # Fix concatenation issues (capital letter after lowercase)
                    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
                    # Clean up extra whitespace
                    text = re.sub(r'\s+', ' ', text).strip()
                # Extract name - take first sentence or first 60 chars
                name = text.split(".")[0] if text else ""
                if len(name) > 60:
                    name = name[:60].rsplit(' ', 1)[0] + "..."
                description = text
                
                product = {
                    "id": product_id,
                    "name": name,
                    "description": description,
                    "brand": brand,
                    "image_url": image_url,
                    "product_url": product_url,
                }
                products.append(product)
            
            return products
        except Exception as e:
            print(f"Error retrieving recent products: {e}")
            return []
    
    async def match_products_to_user(
        self, 
        user_email: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Match products to user taste profile using semantic search."""
        try:
            # Get user preferences to build search query
            from user_preferences import user_preferences
            preferences = await user_preferences.get_user_preferences(user_email)
            
            # Build search query from preferred brands and liked products
            search_terms = []
            if preferences.get("preferred_brands"):
                search_terms.extend(preferences["preferred_brands"])
            if preferences.get("liked_product_ids"):
                # Search for similar products to liked ones
                search_terms.append("similar fashion style")
            
            query = " ".join(search_terms) if search_terms else "fashion clothing products"
            
            # Search for matching products
            memories = await self.search_memories(
                query=query,
                limit=limit * 2  # Get more to filter
            )
            
            # Filter to only products and exclude disliked
            disliked_ids = set(preferences.get("disliked_product_ids", []))
            matched_products = []
            
            for memory in memories:
                memory_id = memory.get("id", "")
                if not memory_id.startswith("product_"):
                    continue
                
                product_id = memory_id.replace("product_", "")
                if product_id in disliked_ids:
                    continue
                
                # Extract product data
                entities = memory.get("entities", [])
                image_url = ""
                product_url = ""
                brand = "unknown"
                
                for entity in entities:
                    if entity.startswith("image_url:"):
                        image_url = entity.split(":", 1)[1]
                    elif entity.startswith("product_url:"):
                        product_url = entity.split(":", 1)[1]
                    elif entity.startswith("brand:"):
                        brand = entity.split(":", 1)[1]
                
                text = memory.get("text", "")
                # Strip HTML if present
                if text:
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
                    # Fix concatenation issues (capital letter after lowercase)
                    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
                    # Clean up extra whitespace
                    text = re.sub(r'\s+', ' ', text).strip()
                # Extract name - take first sentence or first 60 chars
                name = text.split(".")[0] if text else ""
                if len(name) > 60:
                    name = name[:60].rsplit(' ', 1)[0] + "..."
                
                product = {
                    "id": product_id,
                    "name": name,
                    "description": text,
                    "brand": brand,
                    "image_url": image_url,
                    "product_url": product_url,
                    "similarity_score": memory.get("score", 0.0)
                }
                matched_products.append(product)
                
                if len(matched_products) >= limit:
                    break
            
            return matched_products
        except Exception as e:
            print(f"Error matching products to user {user_email}: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global client instance
agent_memory_client = AgentMemoryClient()
