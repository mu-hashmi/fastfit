# Environment Variables - Required vs Optional

## ✅ REQUIRED (Minimum to Run)

**Only ONE variable is required:**

- **`OPENAI_API_KEY`** - Your OpenAI API key
  - Used for: embeddings and semantic search
  - Get it from: https://platform.openai.com/api-keys

## 🔧 OPTIONAL (Have Sensible Defaults)

These work with defaults, but you can override them:

- **`AGENT_MEMORY_SERVER_URL`** - Default: `http://localhost:8001`
- **`AGENT_MEMORY_USER_ID`** - Default: `fastfit_radar`
- **`RSS_POLLING_INTERVAL_SECONDS`** - Default: `600` (10 minutes)
- **`NOTIFICATION_INTERVAL_SECONDS`** - Default: `1800` (30 minutes, reserved for future use)
- **`FRONTEND_URL`** - Default: `http://localhost:3000`
- **`BACKEND_URL`** - Default: `http://localhost:8000`
- **`EMAIL_FROM`** - Default: `FastFit Radar <onboarding@resend.dev>`

### Direct Redis Access (not needed)
- `REDIS_HOST` - Default: `localhost` (not needed, Agent Memory Server handles Redis)
- `REDIS_PORT` - Default: `6379` (not needed)
- `REDIS_PASSWORD` - Default: empty (not needed)

## 📦 OPTIONAL (Only Needed for Email Notifications)

### Resend Email Service (for sending notifications)
- `RESEND_API_KEY` - Only needed if you want to send email notifications
- Get it from: https://resend.com/api-keys

## 🚀 Minimum Setup

To get started, you only need:

```bash
# .env file
OPENAI_API_KEY=sk-your-actual-key-here
```

Then run:
```bash
docker-compose up -d  # Starts Redis + Agent Memory Server
cd backend && uvicorn main:app --reload  # Starts FastAPI
cd frontend && npm run dev  # Starts Next.js
```

## What Works Without Optional Variables

✅ Fetch products from RSS feeds  
✅ Store products in Agent Memory Server  
✅ Match products to user preferences  
✅ Get personalized recommendations via API  
✅ View products in frontend  

❌ Send email notifications (needs Resend API key)

