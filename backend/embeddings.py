"""OpenAI embeddings for products."""
from openai import OpenAI
from typing import List
from config import config

class EmbeddingService:
    """Service for generating embeddings."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text string."""
        try:
            response = self.client.embeddings.create(
                model=config.EMBEDDING_MODEL,
                input=text[:8000]  # Limit text length
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
            else:
                embeddings.append([])
        return embeddings

embedding_service = EmbeddingService()

