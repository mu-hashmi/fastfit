"""User preference management and storage."""
from typing import Dict, Any, List, Optional
from agent_memory_client import agent_memory_client
from embeddings import embedding_service
import numpy as np

class UserPreferences:
    """Manages user preferences and taste profiles."""
    
    async def get_user_preferences(self, email: str) -> Dict[str, Any]:
        """Get user preferences from memory."""
        try:
            # Search for user preferences in memory
            memories = await agent_memory_client.search_memories(
                query=f"user preferences email {email}",
                limit=10,
                user_id_filter=email
            )
            
            if memories:
                # Extract preference data from memory
                for memory in memories:
                    if memory.get("id") == f"user_{email}":
                        return self._parse_preference_memory(memory)
            
            # Return default preferences if not found
            return self._get_default_preferences(email)
        
        except Exception as e:
            print(f"Error getting user preferences for {email}: {e}")
            return self._get_default_preferences(email)
    
    async def store_user_preferences(self, email: str, preferences: Dict[str, Any]) -> bool:
        """Store user preferences in memory."""
        try:
            text = f"User preferences for {email}. Notification frequency: {preferences.get('notification_frequency', 'weekly')}. Preferred brands: {', '.join(preferences.get('preferred_brands', []))}"
            
            memory_data = {
                "id": f"user_{email}",
                "text": text,
                "user_id": email,  # Use email as user_id for user-specific memories
                "memory_type": "semantic",
                "topics": preferences.get("preferred_brands", []),
                "entities": [
                    f"notification_frequency:{preferences.get('notification_frequency', 'weekly')}",
                    f"liked_count:{len(preferences.get('liked_product_ids', []))}",
                    f"disliked_count:{len(preferences.get('disliked_product_ids', []))}"
                ]
            }
            
            response = await agent_memory_client.client.post(
                "/v1/long-term-memory/",
                json={"memories": [memory_data], "deduplicate": True}
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            print(f"Error storing user preferences for {email}: {e}")
            return False
    
    async def update_preferences_from_feedback(
        self, 
        email: str, 
        product_id: str, 
        feedback: str  # "good" or "bad"
    ) -> bool:
        """Update user preferences based on feedback."""
        try:
            preferences = await self.get_user_preferences(email)
            
            if feedback == "good":
                if product_id not in preferences.get("liked_product_ids", []):
                    preferences.setdefault("liked_product_ids", []).append(product_id)
                # Remove from disliked if present
                if product_id in preferences.get("disliked_product_ids", []):
                    preferences["disliked_product_ids"].remove(product_id)
            elif feedback == "bad":
                if product_id not in preferences.get("disliked_product_ids", []):
                    preferences.setdefault("disliked_product_ids", []).append(product_id)
                # Remove from liked if present
                if product_id in preferences.get("liked_product_ids", []):
                    preferences["liked_product_ids"].remove(product_id)
            
            # Rebuild taste profile from liked products
            await self._rebuild_taste_profile(email, preferences)
            
            # Store updated preferences
            return await self.store_user_preferences(email, preferences)
        
        except Exception as e:
            print(f"Error updating preferences from feedback: {e}")
            return False
    
    async def _rebuild_taste_profile(self, email: str, preferences: Dict[str, Any]):
        """Rebuild taste profile embedding from liked products."""
        try:
            liked_ids = preferences.get("liked_product_ids", [])
            if not liked_ids:
                return
            
            # Get embeddings for liked products
            product_embeddings = []
            for product_id in liked_ids[:20]:  # Limit to 20 most recent
                # Search for product in memory
                memories = await agent_memory_client.search_memories(
                    query=f"product {product_id}",
                    limit=1
                )
                if memories:
                    # Extract embedding if available (would need to store separately)
                    # For now, we'll use the product text to build profile
                    pass
            
            # For POC: we'll build taste profile by averaging liked product embeddings
            # This would require storing product embeddings separately
            # For now, we'll use semantic search on liked product IDs
            
        except Exception as e:
            print(f"Error rebuilding taste profile: {e}")
    
    def _parse_preference_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Parse preference data from memory."""
        entities = memory.get("entities", [])
        topics = memory.get("topics", [])
        
        notification_frequency = "weekly"
        for entity in entities:
            if entity.startswith("notification_frequency:"):
                notification_frequency = entity.split(":")[1]
        
        return {
            "email": memory.get("id", "").replace("user_", ""),
            "notification_frequency": notification_frequency,
            "preferred_brands": topics or [],
            "liked_product_ids": [],  # Would need separate storage for this
            "disliked_product_ids": [],  # Would need separate storage for this
        }
    
    def _get_default_preferences(self, email: str) -> Dict[str, Any]:
        """Get default preferences for a new user."""
        return {
            "email": email,
            "notification_frequency": "weekly",
            "preferred_brands": [],
            "liked_product_ids": [],
            "disliked_product_ids": [],
        }

# Global instance
user_preferences = UserPreferences()

