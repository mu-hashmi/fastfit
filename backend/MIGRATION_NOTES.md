# Migration to Redis Agent Memory Server

The project has been updated to use the **Redis Agent Memory Server** instead of direct RedisVL integration.

## What Changed

- **Before**: Direct Redis/RedisVL integration for vector storage
- **After**: Redis Agent Memory Server with REST API for persistent memory

## Benefits

1. **Two-tier Memory System**: Working memory (session-scoped) and long-term memory (persistent)
2. **Semantic Search**: Built-in vector similarity search with metadata filtering
3. **Automatic Features**: Topic extraction, entity recognition, and summarization
4. **REST API**: Clean HTTP interface instead of direct Redis operations
5. **MCP Support**: Can also be accessed via Model Context Protocol

## Files Changed

- `main.py` - Updated to use `agent_memory_client` instead of `redis_client`
- `agent_memory_client.py` - New client for Agent Memory Server (uses httpx)
- `config.py` - Added Agent Memory Server configuration
- `requirements.txt` - Removed redisvl, using httpx for HTTP calls
- `.env.example` - Added Agent Memory Server URL and user ID

## Files Kept (Not Used)

- `redis_client.py` - Kept for reference but no longer imported

## Setup Required

1. Install and run Redis Agent Memory Server (see `AGENT_MEMORY_SETUP.md`)
2. Update `.env` with `AGENT_MEMORY_SERVER_URL` and `AGENT_MEMORY_USER_ID`
3. Ensure the Agent Memory Server is running before starting FastAPI

## API Changes

All endpoints remain the same, but internally:
- `POST /api/store-products` - Now stores products to Agent Memory Server
- `GET /api/products` - Now retrieves from Agent Memory Server using semantic search
- `GET /api/user/{email}/matches` - Uses Agent Memory Server for product matching
- `POST /api/match-products/{email}` - Uses Agent Memory Server for semantic search

## Memory Structure

Products are stored as long-term memories with:
- `id`: `product_{product_id}` (unique identifier)
- `text`: Product name + description
- `user_id`: "fastfit_radar" (configurable)
- `memory_type`: "semantic"
- `topics`: Brand name (e.g., ["Adidas"])
- `entities`: Contains product_id, image_url, product_url, brand

User preferences are stored as:
- `id`: `user_{email}`
- `memory_type`: "semantic"
- `topics`: Preferred brands
- `entities`: notification_frequency, liked_count, disliked_count

