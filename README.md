# FastFit Radar

An agent-driven **personalized clothing notification system** that monitors brand new releases from RSS feeds, stores products in Redis Memory, learns user preferences from feedback, and sends personalized email notifications based on individual taste profiles.

## Architecture

- **Backend**: FastAPI (Python) with Redis Agent Memory Server
- **Frontend**: Next.js with TailwindCSS (email subscription + preference management)
- **Integrations**: 
  - Redis Agent Memory Server (RedisVL) for persistent memory with semantic search
  - RSS feed polling for brand new releases
  - OpenAI for embeddings and product matching
  - Email service (SendGrid/Resend) for notifications

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Redis server running locally
- Redis Agent Memory Server (see setup instructions below)
- OpenAI API key
- Resend API key (optional, for email notifications)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` in the project root and add your API keys:
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `RESEND_API_KEY` - Your Resend API key (optional, for email notifications)

6. Start Redis server:
```bash
redis-server
```

7. Create `.env` file and start Redis and Agent Memory Server:
```bash
# From project root, create .env file
cp .env.example .env

# Edit .env and add your OPENAI_API_KEY
# Then start services (docker-compose reads .env automatically)
docker-compose up -d
```

8. Run the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies (already done if you used create-next-app):
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Continuous Polling System

The system runs **automatically** in the background with polling loops:

### 1. RSS Feed Polling Loop (every 10 minutes by default)
- Fetches new products from fashion brand RSS feeds
- Filters out already-processed products to avoid duplicates
- Embeds and stores new products in Redis Memory via Agent Memory Server
- Tracks processed products to maintain efficiency

### 2. Notification Matching (Manual/Planned)
- Currently, notifications can be sent manually via API endpoints
- Future: Automatic notification loop that matches products to users and sends emails
- Respects user frequency settings (daily/weekly/realtime)

### Monitored RSS Feeds

The system polls these fashion brand RSS feeds:
- **Adidas** - News and releases RSS
- **HYPEBEAST** - Fashion, footwear, tech RSS
- **Luxury Daily** - Luxury brand news aggregator
- Additional feeds can be added via configuration

### Configuration

You can adjust polling intervals via environment variables:
- `RSS_POLLING_INTERVAL_SECONDS` - How often to poll RSS feeds (default: 600 = 10 minutes)
- `NOTIFICATION_INTERVAL_SECONDS` - Reserved for future automatic notification loop (default: 1800 = 30 minutes)

## API Endpoints

### Main Endpoints
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/polling-status` - Get polling service status and statistics

### User Subscription Endpoints
- `POST /api/subscribe` - Subscribe user with email and notification preferences
- `GET /api/user/{email}/preferences` - Get user preferences
- `PUT /api/user/{email}/preferences` - Update user preferences

### Product Endpoints
- `GET /api/products` - Get latest products (for frontend display)
- `GET /api/user/{email}/matches` - Get personalized product matches for user

### Manual Workflow Endpoints (for testing/debugging)
- `POST /api/fetch-rss` - Fetch products from RSS feeds manually
- `POST /api/store-products` - Store products in Agent Memory Server manually
- `POST /api/match-products/{email}` - Match products for user manually

### Feedback Endpoints
- `POST /api/user/{email}/feedback` - Record user feedback (good/bad on products)
- `GET /api/user/{email}/feedback/click` - Record feedback from email click (redirects to thank you page)

## Project Structure

```
agent-hackathon-sf/
├── backend/
│   ├── main.py              # FastAPI application (starts polling service on startup)
│   ├── polling_service.py   # Background polling service for RSS feed polling
│   ├── config.py            # Configuration (RSS feeds, intervals, etc.)
│   ├── agent_memory_client.py  # Redis Agent Memory Server client
│   ├── rss_fetcher.py       # RSS feed fetcher for fashion brands
│   ├── embeddings.py        # OpenAI embeddings service
│   ├── user_preferences.py  # User preference management
│   ├── email_service.py     # Email notification service (Resend)
│   ├── redis_client.py      # Legacy Redis client (kept for reference)
│   ├── requirements.txt     # Python dependencies
│   └── AGENT_MEMORY_SETUP.md  # Agent Memory Server setup guide
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main page
│   │   ├── components/      # React components
│   │   └── layout.tsx       # Root layout
│   └── package.json         # Node dependencies
├── docker-compose.yml       # Docker Compose for Redis + Agent Memory Server
└── AGENTS.md                 # Agent instructions

```

## Usage

1. Start both backend and frontend servers
2. The backend **automatically starts polling** RSS feeds when it starts
3. Open `http://localhost:3000` in your browser
4. Enter your email to subscribe and set notification preferences
5. The system will:
   - Fetch new products from RSS feeds automatically
   - Build your taste profile as you provide feedback
   - Send personalized notifications based on your preferences
6. Click "good" or "bad" on products in emails to improve recommendations

**The system learns your preferences over time** - more feedback = better matches!

## Notes

- The system is designed for personalization and reliability
- All outputs are JSON-first and deterministic
- Products are sourced from real RSS feeds
- User preferences are learned from feedback (good/bad clicks)
- Error handling is graceful - failures don't crash the system
- Email notifications respect user frequency preferences (daily/weekly/realtime)

