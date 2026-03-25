# Frontend - AI Logging Agent

This is the Next.js frontend for the AI Logging Agent project. It provides a chat-based interface for interacting with the FastAPI backend and viewing agent responses.

## Stack

- Next.js 16 + React 19
- TypeScript
- Tailwind CSS 4
- shadcn/ui components

## Prerequisites

- Node.js 18+ (20+ recommended)
- `pnpm` installed globally
- Backend running on `http://localhost:8000` (or another configured URL)

## Setup

```bash
pnpm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Production Build

```bash
pnpm build
pnpm start
```

## Linting

```bash
pnpm lint
```

## Key Files

- `app/page.tsx` - App entry page
- `components/chat.tsx` - Main chat container
- `components/chat/sidebar.tsx` - Session and quick-prompt sidebar
- `components/chat/message-bubble.tsx` - Message rendering
- `lib/api.ts` - Backend API client
- `lib/hooks/use-sessions.ts` - Session persistence

## Notes

- Session history is stored in browser local storage.
- The frontend is intentionally decoupled from backend internals and communicates only through HTTP endpoints.
