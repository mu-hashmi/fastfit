# Redis Agent Memory Server Setup

FastFit Radar uses the Redis Agent Memory Server for persistent memory storage with semantic search capabilities.

## Quick Start with Docker Compose (Recommended)

The easiest way to run everything is using Docker Compose from the project root:

1. **Create a `.env` file in the project root:**
```bash
# From project root
cp .env.example .env
```

2. **Edit `.env` and add your OpenAI API key:**
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

3. **Run docker-compose (it will automatically read from .env):**
```bash
docker-compose up -d
```

That's it! Docker Compose automatically reads variables from the `.env` file in the same directory.

This will start:
- Redis on port 6379
- Agent Memory Server on port 8001

4. **Check that everything is running:**
```bash
docker-compose ps
```

5. **View logs:**
```bash
docker-compose logs -f agent-memory-server
```

6. **Stop everything:**
```bash
docker-compose down
```

## Manual Installation (Alternative)

If you prefer to run without Docker Compose:

1. **Clone the Agent Memory Server repository:**
```bash
cd /tmp  # or any directory outside your project
git clone https://github.com/redis/agent-memory-server.git
cd agent-memory-server
```

2. **Install dependencies:**
```bash
pip install uv
uv install --all-extras
```

3. **Set up environment variables:**
Create a `.env` file in the agent-memory-server directory:
```bash
DISABLE_AUTH=true
REDIS_URL=redis://localhost:6379
LONG_TERM_MEMORY=true
ENABLE_DISCRETE_MEMORY_EXTRACTION=true
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Start Redis (if not already running):**
```bash
redis-server
# Or using Docker:
docker run -d --name redis -p 6379:6379 redis:latest
```

5. **Start the Agent Memory Server:**
```bash
uv run agent-memory api --no-worker --port 8001
```

The server will be available at `http://localhost:8001`

## Configuration

Update your FastFit Radar `.env` file:
```bash
AGENT_MEMORY_SERVER_URL=http://localhost:8001
AGENT_MEMORY_USER_ID=fastfit_radar
```

## Features Used

- **Long-term Memory**: Products from RSS feeds are stored as long-term memories
- **Semantic Search**: Products are searchable using vector similarity
- **Metadata Filtering**: Products include metadata (brand, image_url, product_url, etc.)
- **User Preferences**: User taste profiles and preferences are stored as memories

## API Endpoints Used

- `POST /api/v1/memories/long-term` - Store memories
- `GET /api/v1/memories/long-term/search` - Search memories

## Using Individual Docker Containers (Alternative)

If you prefer to run containers individually instead of docker-compose:

**Option 1: Redis running on host machine:**
```bash
docker run -d \
  --name agent-memory-server \
  -p 8001:8000 \
  -e DISABLE_AUTH=true \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  -e LONG_TERM_MEMORY=true \
  -e ENABLE_DISCRETE_MEMORY_EXTRACTION=true \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  redislabs/agent-memory-server:latest
```

**Option 2: Redis also running in Docker (using Docker network):**
```bash
# First, create a network (if not exists)
docker network create redis-network

# Run Redis in the network
docker run -d --name redis --network redis-network redis:latest

# Run Agent Memory Server in the same network
docker run -d \
  --name agent-memory-server \
  --network redis-network \
  -p 8001:8000 \
  -e DISABLE_AUTH=true \
  -e REDIS_URL=redis://redis:6379 \
  -e LONG_TERM_MEMORY=true \
  -e ENABLE_DISCRETE_MEMORY_EXTRACTION=true \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  redislabs/agent-memory-server:latest
```

## Troubleshooting

- Make sure Redis is running before starting the Agent Memory Server
- Check that the server is accessible at the configured URL
- Verify OpenAI API key is set correctly
- Check server logs for any errors

