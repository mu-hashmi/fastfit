"""Redis and RedisVL client setup."""
import redis
from redisvl import RedisVL
from redisvl.index import SearchIndex
from redisvl.schema import IndexSchema
from typing import List, Dict, Any, Optional
import json
from config import config

class RedisClient:
    """Redis client wrapper for FastFit Radar."""
    
    def __init__(self):
        """Initialize Redis connection."""
        redis_url = f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}"
        if config.REDIS_PASSWORD:
            redis_url = f"redis://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"
        
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
            decode_responses=False  # Keep binary for vector storage
        )
        self.rvl = RedisVL(redis_url=redis_url)
        self._ensure_index()
    
    def _ensure_index(self):
        """Create vector index if it doesn't exist."""
        schema = IndexSchema.from_dict({
            "index": {
                "name": config.VECTOR_INDEX_NAME,
                "prefix": f"{config.VECTOR_INDEX_NAME}:",
            },
            "fields": [
                {
                    "name": "id",
                    "type": "tag"
                },
                {
                    "name": "text",
                    "type": "text"
                },
                {
                    "name": "subreddit",
                    "type": "tag"
                },
                {
                    "name": "score",
                    "type": "numeric"
                },
                {
                    "name": "embedding",
                    "type": "vector",
                    "attrs": {
                        "dims": config.EMBEDDING_DIMENSION,
                        "algorithm": "HNSW",
                        "distance_metric": "COSINE"
                    }
                }
            ]
        })
        
        try:
            index = SearchIndex.from_dict(schema.to_dict())
            index.connect(self.rvl)
            if not index.exists():
                index.create()
                print(f"Created vector index: {config.VECTOR_INDEX_NAME}")
            else:
                print(f"Vector index exists: {config.VECTOR_INDEX_NAME}")
        except Exception as e:
            print(f"Index creation/check error: {e}")
            # Fallback to simple Redis storage if RedisVL fails
            print("Falling back to simple Redis storage")
    
    def store_post(self, post: Dict[str, Any]) -> bool:
        """Store a Reddit post with embedding in Redis."""
        try:
            key = f"{config.VECTOR_INDEX_NAME}:{post['id']}"
            
            # Store as hash for simple retrieval
            self.redis_client.hset(key, mapping={
                "id": post["id"],
                "text": post["text"],
                "subreddit": post["subreddit"],
                "score": str(post["score"]),
            })
            
            # Store embedding separately for vector search
            embedding_key = f"{key}:embedding"
            embedding_bytes = json.dumps(post["embedding"]).encode('utf-8')
            self.redis_client.set(embedding_key, embedding_bytes)
            
            # Try to use RedisVL for vector storage
            try:
                index = SearchIndex.from_dict({
                    "index": {"name": config.VECTOR_INDEX_NAME},
                    "fields": [{"name": "embedding", "type": "vector", "attrs": {
                        "dims": config.EMBEDDING_DIMENSION,
                        "algorithm": "HNSW",
                        "distance_metric": "COSINE"
                    }}]
                })
                index.connect(self.rvl)
                
                # Store document with vector
                doc = {
                    "id": post["id"],
                    "text": post["text"],
                    "subreddit": post["subreddit"],
                    "score": post["score"],
                    "embedding": post["embedding"]
                }
                index.add([doc])
            except Exception as e:
                # If RedisVL fails, we still have the data in Redis
                print(f"RedisVL storage failed (non-critical): {e}")
            
            return True
        except Exception as e:
            print(f"Error storing post {post['id']}: {e}")
            return False
    
    def retrieve_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent posts from Redis."""
        try:
            keys = self.redis_client.keys(f"{config.VECTOR_INDEX_NAME}:*")
            # Filter out embedding keys
            post_keys = []
            for k in keys:
                k_str = k.decode() if isinstance(k, bytes) else k
                if not k_str.endswith(':embedding'):
                    post_keys.append(k_str)
            
            posts = []
            for key in post_keys[:limit]:
                data = self.redis_client.hgetall(key)
                if data:
                    post = {}
                    for k, v in data.items():
                        k_str = k.decode() if isinstance(k, bytes) else k
                        v_str = v.decode() if isinstance(v, bytes) else v
                        post[k_str] = v_str
                    
                    # Get embedding
                    embedding_key = f"{key}:embedding"
                    embedding_data = self.redis_client.get(embedding_key)
                    if embedding_data:
                        embedding_str = embedding_data.decode('utf-8') if isinstance(embedding_data, bytes) else embedding_data
                        post["embedding"] = json.loads(embedding_str)
                    else:
                        post["embedding"] = []
                    
                    post["score"] = int(post.get("score", 0))
                    posts.append(post)
            
            return sorted(posts, key=lambda x: x.get("score", 0), reverse=True)
        except Exception as e:
            print(f"Error retrieving posts: {e}")
            return []
    
    def search_similar(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar posts using vector similarity."""
        try:
            index = SearchIndex.from_dict({
                "index": {"name": config.VECTOR_INDEX_NAME},
                "fields": [{"name": "embedding", "type": "vector", "attrs": {
                    "dims": config.EMBEDDING_DIMENSION,
                    "algorithm": "HNSW",
                    "distance_metric": "COSINE"
                }}]
            })
            index.connect(self.rvl)
            
            results = index.query(
                vector=query_embedding,
                return_fields=["id", "text", "subreddit", "score"],
                limit=limit
            )
            return results
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []

redis_client = RedisClient()

