# AI Logging Agent

An AI-powered log analysis system for DevOps teams. This project provides an intelligent agent that analyzes application logs, identifies issues, and provides actionable insights.

## What It Does

The AI Logging Agent is a Level 1 log analysis system that:

- **Lists available log files** in a configured directory
- **Reads and analyzes log file contents** to identify errors, warnings, and patterns
- **Searches logs** for specific terms or patterns
- **Saves analysis summaries** to a markdown file
- **Provides a chat interface** for natural language interaction with your logs

The agent uses Google Gemini AI (via LiteLLM) to understand log content and provide intelligent analysis with root cause identification and actionable recommendations.

## Project Structure

```
ai-logging-agent/
├── backend/          # Python FastAPI backend with AI agent
│   ├── main.py       # FastAPI application entry point
│   ├── src/
│   │   ├── agents/   # Log analyzer agent implementation
│   │   ├── tools/    # Log manipulation tools
│   │   ├── config.py # Configuration management
│   │   └── utils/    # Utility functions
│   └── pyproject.toml
│
├── frontend/         # Next.js frontend
│   ├── app/          # Next.js app directory
│   ├── components/   # React components (chat UI)
│   └── package.json
│
└── README.md         # This file
```

## Tech Stack

**Backend:**

- Python 3.12+
- FastAPI (web framework)
- OpenAI Agents SDK with LiteLLM integration
- Google Gemini AI (default model)

**Frontend:**

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui components

## Quick Start

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Node.js 18+ (or pnpm/bun)
- Google Gemini API key

### 1. Backend Setup

#### Using uv (Recommended)

```bash
cd backend

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and sync the virtual environment automatically
uv sync

# Create .env file with your configuration
cp .env.example .env  # If .env.example exists
# Or create .env manually (see Environment Variables section below)

# Create logs directory and add your log files
mkdir -p logs
# Place your .log files in the logs/ directory

# Start the backend server
uv run main.py
# Backend runs at http://localhost:8000
```

#### Using pip (Alternative)

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Create .env and start
cp .env.example .env
mkdir -p logs
python main.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or: pnpm install / bun install

# Create .env.local file
cp .env.example .env.local  # If .env.example exists
# Or create .env.local manually (see Frontend Environment Variables below)

# Start development server
npm run dev
# Frontend runs at http://localhost:3000
```

### 3. Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory. There is only **one required variable** — the backend API URL:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Update this value if your backend is running on a different host or port (e.g., in production or Docker).

## Running the Project

Start services in this order:

**Step 1 — Start the backend:**

```bash
cd backend
uv run main.py
```

**Step 2 — Start the frontend:**

```bash
cd frontend
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. Place your log files (`.log` extension) in the `backend/logs/` directory
2. Start both backend and frontend servers (see above)
3. Open [http://localhost:3000](http://localhost:3000) in your browser
4. Use the chat interface to interact with the AI agent:
   - "What log files are available?"
   - "Analyze the errors in app.log"
   - "Search for 'timeout' in system.log"

## API Endpoints

**Backend (port 8000):**

| Endpoint  | Method | Description                    |
|-----------|--------|--------------------------------|
| `/chat`   | POST   | Send a message to the AI agent |
| `/health` | GET    | Health check endpoint          |

## Development

### Backend Development

```bash
cd backend
uv run main.py  # Runs with uvicorn hot reload
```

### Frontend Development

```bash
cd frontend
npm run dev    # Development server with hot reload
npm run build  # Production build
npm run lint   # Run ESLint
```

## License

MIT

---

## Roadmap

This agent is currently at **Level 1** — focused on reactive log analysis through a conversational interface.

Planned integrations for future levels:

- **Level 2 — Reasoning Agents:** Incorporate multi-step reasoning agents capable of deeper root cause analysis, hypothesis generation, and autonomous investigation across multiple log sources.
- **Level 3 — Temporal Integration:** Add time-series awareness so the agent can detect anomalies, trends, and correlations across log history, enabling proactive alerting and predictive insights.
