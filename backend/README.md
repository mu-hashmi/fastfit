# FastFit Radar Backend

FastAPI backend for the FastFit Radar personalized clothing notification system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` in the project root and fill in your API keys:
```bash
cd ..  # Go to project root
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. Make sure Redis and Agent Memory Server are running (use docker-compose from project root):
```bash
docker-compose up -d
```

4. Run the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Main Endpoints
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/polling-status` - Get polling service status

### User Subscription Endpoints
- `POST /api/subscribe` - Subscribe user with email and notification preferences
- `GET /api/user/{email}/preferences` - Get user preferences
- `PUT /api/user/{email}/preferences` - Update user preferences
- `POST /api/user/{email}/feedback` - Record user feedback (good/bad on products)

### Product Endpoints
- `GET /api/products` - Get latest products
- `POST /api/fetch-rss` - Fetch products from RSS feeds manually
- `POST /api/store-products` - Store products in Agent Memory Server manually
- `GET /api/user/{email}/matches` - Get personalized product matches for user
- `POST /api/match-products/{email}` - Match products for user manually

### Feedback Endpoints
- `POST /api/user/{email}/feedback` - Record user feedback (good/bad on products)
- `GET /api/user/{email}/feedback/click` - Record feedback from email click (redirects to thank you page)

## Environment Variables

See `.env.example` in the project root for required environment variables. The backend reads from the root `.env` file.
