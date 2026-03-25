# Quickstart: Interactive Textbook Generation

## Prerequisites

- Node.js 18+
- Python 3.12
- Git

## Environment Variables

Create `.env` files in both backend and frontend:

### Backend (.env)
```
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
DATABASE_URL=your_neon_database_url
BETTER_AUTH_SECRET=your_auth_secret
BETTER_AUTH_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Local Development

### 1. Backend Setup
```bash
cd projects/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using Prisma)
npx prisma migrate dev

# Start backend
uvicorn src.main:app --reload
```

Backend runs at http://localhost:8000

### 2. Frontend Setup
```bash
cd projects/website

# Install dependencies
npm install

# Start development server
npm run start
```

Frontend runs at http://localhost:3000

### 3. RAG Indexing (one-time setup)
```bash
cd projects/rag

# Index textbook content to Qdrant
python -m rag.indexer
```

## Testing

### Backend Tests
```bash
cd projects/backend
pytest
```

### Frontend Build Test
```bash
cd projects/website
npm run build
```

## Deployment

See Constitution Section XII for deployment targets:

| Service | Platform | Method |
|---------|----------|--------|
| Website | Vercel | GitHub push to main |
| Backend | Railway | Docker deploy |
| Vectors | Qdrant Cloud | Managed |
| Database | Neon | Managed |

## Verification Checklist

- [ ] Backend /health returns 200
- [ ] Frontend loads at localhost:3000
- [ ] Can navigate between chapters
- [ ] Chatbot responds with citations
- [ ] User can sign up and log in
- [ ] Background preference saves
- [ ] Quiz loads and submits
- [ ] Mobile layout works at 375px