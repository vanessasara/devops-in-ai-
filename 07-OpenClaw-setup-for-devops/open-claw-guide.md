# OpenClaw + WhatsApp Integration Guide
## Building an AI Employee / Digital FTE

> **Purpose:** A comprehensive step-by-step guide covering OpenClaw installation, environment configuration, WhatsApp Business API integration, and deploying a fully autonomous AI Employee (Digital Full-Time Equivalent).

---

## Table of Contents

1. [Overview & Architecture](#1-overview--architecture)
2. [Prerequisites](#2-prerequisites)
3. [OpenClaw Installation](#3-openclaw-installation)
4. [Environment Configuration](#4-environment-configuration)
5. [WhatsApp Business API Setup](#5-whatsapp-business-api-setup)
6. [Connecting OpenClaw to WhatsApp](#6-connecting-openclaw-to-whatsapp)
7. [Building Your AI Employee Agent](#7-building-your-ai-employee-agent)
8. [Tool & Skill Configuration](#8-tool--skill-configuration)
9. [Workflow Automation (Agentic Pipelines)](#9-workflow-automation-agentic-pipelines)
10. [Deployment & Scaling](#10-deployment--scaling)
11. [Monitoring & Observability](#11-monitoring--observability)
12. [Security & Compliance](#12-security--compliance)
13. [Troubleshooting](#13-troubleshooting)
14. [Reference: Environment Variables](#14-reference-environment-variables)

---

## 1. Overview & Architecture

### What is OpenClaw?

**OpenClaw** is an open-source agentic AI framework designed for deploying autonomous AI employees. It provides:

- Multi-LLM routing (OpenAI, Claude, Gemini, local models)
- Tool/function calling with MCP (Model Context Protocol) support
- Persistent memory and session management
- Multi-channel connectors (WhatsApp, Slack, Email, Web)
- Workflow orchestration for long-running tasks

### Digital FTE Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INCOMING CHANNELS                     │
│   WhatsApp Business API  │  Slack  │  Email  │  Web      │
└──────────────┬──────────────────────────────────────────┘
               │  Webhook Events
               ▼
┌─────────────────────────────────────────────────────────┐
│                  OpenClaw Gateway Layer                  │
│         Message Router  │  Session Manager              │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│               AI Employee Agent Core                     │
│   LLM Brain (OpenAI / Claude)  │  Memory Store          │
│   Tool Executor                │  Context Manager        │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│                    Integrations & Tools                  │
│  CRM  │  Calendar  │  Databases  │  APIs  │  File Store  │
└─────────────────────────────────────────────────────────┘
```

### Key Concepts

| Term | Description |
|------|-------------|
| **Digital FTE** | An AI agent that performs tasks like a full-time employee — autonomously, continuously, and scalably |
| **AI Employee** | The configured OpenClaw agent persona with role, memory, tools, and escalation logic |
| **Session** | A persistent conversation context tied to a user/phone number |
| **Tool** | A function the agent can call (e.g., check calendar, create ticket, send email) |
| **Handoff** | Escalation from AI to a human agent when confidence is low |

---

## 2. Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Ubuntu 22.04 / macOS 13 | Ubuntu 24.04 LTS |
| CPU | 2 vCPU | 4+ vCPU |
| RAM | 4 GB | 8–16 GB |
| Storage | 20 GB | 50 GB SSD |
| Node.js | v18.x | v20.x LTS |
| Python | 3.10+ | 3.11+ |
| Docker | 24.x | 25.x |

### Accounts & API Keys Required

- [ ] **OpenAI API Key** — [platform.openai.com](https://platform.openai.com) (or Anthropic/Gemini)
- [ ] **Meta Developer Account** — [developers.facebook.com](https://developers.facebook.com)
- [ ] **WhatsApp Business Account** — verified business phone number
- [ ] **WhatsApp Business API Access** — via Meta or a BSP (Business Solution Provider)
- [ ] **Redis** — for session/memory store (local or cloud like Upstash)
- [ ] **PostgreSQL** — for persistent agent memory and audit logs

### Install Base Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify Node.js
node --version   # v20.x.x
npm --version    # 10.x.x

# Install Python 3.11 + uv (fast package manager)
sudo apt install -y python3.11 python3.11-venv python3-pip
pip install uv --break-system-packages

# Install Docker
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker
docker --version
docker compose version

# Install Git
sudo apt install -y git curl wget jq
```

---

## 3. OpenClaw Installation

### 3.1 Clone the Repository

```bash
# Clone OpenClaw
git clone https://github.com/openclaw-ai/openclaw.git
cd openclaw

# Or install globally via npm
npm install -g @openclaw/cli

# Verify installation
openclaw --version
```

### 3.2 Project Initialization

```bash
# Initialize a new AI Employee project
openclaw init my-ai-employee

cd my-ai-employee

# Project structure created:
# my-ai-employee/
# ├── .env
# ├── openclaw.config.ts
# ├── agents/
# │   └── employee.agent.ts
# ├── tools/
# │   └── index.ts
# ├── memory/
# │   └── store.ts
# ├── channels/
# │   └── whatsapp.ts
# ├── workflows/
# │   └── index.ts
# ├── docker-compose.yml
# └── package.json
```

### 3.3 Install Node Dependencies

```bash
npm install

# Or using pnpm (faster, recommended)
npm install -g pnpm
pnpm install
```

### 3.4 Install Python Dependencies (for LLM/Agent backend)

```bash
# Create virtual environment
uv venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install OpenClaw Python SDK + dependencies
uv pip install openclaw-sdk openai anthropic langchain langgraph
uv pip install fastapi uvicorn redis psycopg2-binary python-dotenv
uv pip install httpx pydantic temporalio  # optional: Temporal for workflows

# Verify
python -c "import openclaw; print(openclaw.__version__)"
```

### 3.5 Start Infrastructure Services

```bash
# Start Redis + PostgreSQL with Docker Compose
cat > docker-compose.yml << 'EOF'
version: '3.9'

services:
  redis:
    image: redis:7-alpine
    container_name: openclaw-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    container_name: openclaw-postgres
    environment:
      POSTGRES_USER: openclaw
      POSTGRES_PASSWORD: openclaw_secret
      POSTGRES_DB: openclaw_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
EOF

docker compose up -d

# Verify services are running
docker compose ps
```

---

## 4. Environment Configuration

### 4.1 Create the `.env` File

```bash
cp .env.example .env
nano .env   # or use your preferred editor
```

### 4.2 Full `.env` Configuration

```dotenv
# ============================================================
# OpenClaw Core Configuration
# ============================================================
OPENCLAW_ENV=production
OPENCLAW_PORT=3000
OPENCLAW_SECRET=your_super_secret_key_change_this

# ============================================================
# LLM Provider (choose one or configure fallback chain)
# ============================================================
LLM_PROVIDER=openai                   # openai | anthropic | gemini | local
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
OPENAI_MODEL=gpt-4o                   # gpt-4o | gpt-4-turbo | gpt-3.5-turbo

# Anthropic (optional fallback)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Gemini (optional fallback)
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-1.5-pro

# LiteLLM routing (optional — for multi-model load balancing)
LITELLM_MASTER_KEY=sk-lite-xxxxxxxxxx
LITELLM_BASE_URL=http://localhost:4000

# ============================================================
# WhatsApp Business API
# ============================================================
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxx
WHATSAPP_WEBHOOK_VERIFY_TOKEN=my_custom_verify_token_123
WHATSAPP_API_VERSION=v20.0
WHATSAPP_BASE_URL=https://graph.facebook.com

# ============================================================
# Session & Memory Store
# ============================================================
REDIS_URL=redis://localhost:6379
REDIS_SESSION_TTL=86400              # Session TTL in seconds (24h)

# ============================================================
# Database (Persistent Memory + Audit Logs)
# ============================================================
DATABASE_URL=postgresql://openclaw:openclaw_secret@localhost:5432/openclaw_db

# ============================================================
# AI Employee Configuration
# ============================================================
AGENT_NAME=Alex
AGENT_ROLE=Customer Support Specialist
AGENT_COMPANY=Acme Corp
AGENT_TIMEZONE=Asia/Karachi
AGENT_MAX_TOKENS=4096
AGENT_TEMPERATURE=0.3
AGENT_ESCALATION_THRESHOLD=0.4       # Confidence score below which agent escalates

# ============================================================
# Webhook & Public URL
# ============================================================
PUBLIC_URL=https://your-domain.com   # Must be HTTPS for WhatsApp webhooks
# Use ngrok for local development:   https://xxxx.ngrok.io

# ============================================================
# Integrations (optional — enable as needed)
# ============================================================
GOOGLE_CALENDAR_CLIENT_ID=
GOOGLE_CALENDAR_CLIENT_SECRET=
NOTION_API_KEY=
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxx
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
```

---

## 5. WhatsApp Business API Setup

### 5.1 Create a Meta Developer App

```
1. Go to https://developers.facebook.com/apps
2. Click "Create App"
3. Select "Business" as app type
4. Fill in App Name: "My AI Employee"
5. Add your Business Account
6. Click "Create App"
```

### 5.2 Add WhatsApp Product

```
1. In your app dashboard → "Add a Product"
2. Find "WhatsApp" → click "Set Up"
3. Select or create a WhatsApp Business Account (WABA)
4. Note your:
   - Phone Number ID  (WHATSAPP_PHONE_NUMBER_ID)
   - WhatsApp Business Account ID (WHATSAPP_BUSINESS_ACCOUNT_ID)
```

### 5.3 Generate a Permanent Access Token

```bash
# Option A: Use Meta's System User (recommended for production)
# 1. Go to Business Settings → System Users → Add
# 2. Assign WhatsApp app with "Full Control"
# 3. Generate token → copy to WHATSAPP_ACCESS_TOKEN in .env

# Option B: Use Graph API Explorer (testing only — short-lived)
# https://developers.facebook.com/tools/explorer
# Select your app → Generate User Access Token → Add whatsapp_business_messaging permission
```

### 5.4 Configure Webhook

```bash
# Your webhook URL format:
# https://your-domain.com/webhooks/whatsapp

# For local development, use ngrok:
npm install -g ngrok
ngrok http 3000
# Copy the https URL e.g. https://abc123.ngrok.io
```

```
In Meta Developer Console:
1. WhatsApp → Configuration → Webhooks
2. Callback URL: https://your-domain.com/webhooks/whatsapp
3. Verify Token: (must match WHATSAPP_WEBHOOK_VERIFY_TOKEN in .env)
4. Click "Verify and Save"
5. Subscribe to fields:
   ✅ messages
   ✅ message_deliveries
   ✅ message_reads
   ✅ messaging_postbacks
```

### 5.5 Test WhatsApp API Connection

```bash
# Send a test message via curl
curl -X POST \
  "https://graph.facebook.com/v20.0/$WHATSAPP_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "+923001234567",
    "type": "text",
    "text": { "body": "Hello! AI Employee test message." }
  }'

# Expected response:
# {"messaging_product":"whatsapp","contacts":[{"input":"...","wa_id":"..."}],"messages":[{"id":"..."}]}
```

---

## 6. Connecting OpenClaw to WhatsApp

### 6.1 WhatsApp Channel Configuration

```typescript
// channels/whatsapp.ts

import { WhatsAppChannel, OpenClaw } from '@openclaw/sdk';

export const whatsappChannel = new WhatsAppChannel({
  phoneNumberId: process.env.WHATSAPP_PHONE_NUMBER_ID!,
  businessAccountId: process.env.WHATSAPP_BUSINESS_ACCOUNT_ID!,
  accessToken: process.env.WHATSAPP_ACCESS_TOKEN!,
  webhookVerifyToken: process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN!,
  apiVersion: process.env.WHATSAPP_API_VERSION || 'v20.0',

  // Message handling options
  options: {
    typingIndicator: true,          // Show "typing..." while AI processes
    readReceipts: true,             // Mark messages as read on receive
    deliveryReceipts: true,
    maxRetries: 3,
    retryDelay: 1000,               // ms between retries
    sessionTimeout: 30 * 60,        // 30 minutes inactivity timeout
  },

  // Media handling
  media: {
    allowImages: true,
    allowDocuments: true,
    allowAudio: true,
    maxFileSizeMB: 16,
  }
});
```

### 6.2 Webhook Handler

```typescript
// src/webhooks/whatsapp.webhook.ts

import { Router, Request, Response } from 'express';
import { OpenClawAgent } from '../agents/employee.agent';

const router = Router();

// Webhook verification (GET) — Meta pings this when you set up the webhook
router.get('/webhooks/whatsapp', (req: Request, res: Response) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN) {
    console.log('✅ WhatsApp Webhook verified');
    res.status(200).send(challenge);
  } else {
    res.status(403).send('Forbidden');
  }
});

// Incoming messages (POST)
router.post('/webhooks/whatsapp', async (req: Request, res: Response) => {
  // Always respond 200 immediately — WhatsApp will retry if no response within 5s
  res.status(200).send('OK');

  try {
    const body = req.body;

    if (body.object !== 'whatsapp_business_account') return;

    for (const entry of body.entry || []) {
      for (const change of entry.changes || []) {
        const value = change.value;

        if (!value?.messages) continue;

        for (const message of value.messages) {
          const from = message.from;           // Sender's WhatsApp number
          const messageId = message.id;
          const timestamp = message.timestamp;

          let userInput = '';

          // Handle different message types
          switch (message.type) {
            case 'text':
              userInput = message.text.body;
              break;
            case 'image':
              userInput = `[Image received: ${message.image?.caption || 'no caption'}]`;
              break;
            case 'document':
              userInput = `[Document received: ${message.document?.filename}]`;
              break;
            case 'audio':
              userInput = `[Voice message received]`;
              break;
            case 'interactive':
              // Button reply or list reply
              userInput = message.interactive?.button_reply?.title ||
                          message.interactive?.list_reply?.title || '';
              break;
            default:
              userInput = `[Unsupported message type: ${message.type}]`;
          }

          // Process with AI Employee
          await OpenClawAgent.handleMessage({
            channel: 'whatsapp',
            userId: from,
            messageId,
            content: userInput,
            timestamp: new Date(parseInt(timestamp) * 1000),
            rawMessage: message,
            metadata: {
              phoneNumberId: value.metadata?.phone_number_id,
              displayPhoneNumber: value.metadata?.display_phone_number,
            }
          });
        }
      }
    }
  } catch (error) {
    console.error('Webhook processing error:', error);
  }
});

export default router;
```

### 6.3 Sending Messages Back to WhatsApp

```typescript
// utils/whatsapp.sender.ts

import axios from 'axios';

const WA_API = `https://graph.facebook.com/${process.env.WHATSAPP_API_VERSION}`;

export class WhatsAppSender {

  // Send plain text message
  static async sendText(to: string, text: string): Promise<void> {
    await axios.post(
      `${WA_API}/${process.env.WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: 'whatsapp',
        recipient_type: 'individual',
        to,
        type: 'text',
        text: { body: text, preview_url: true }
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.WHATSAPP_ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
  }

  // Send interactive buttons (up to 3 buttons)
  static async sendButtons(to: string, body: string, buttons: { id: string; title: string }[]): Promise<void> {
    await axios.post(
      `${WA_API}/${process.env.WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: 'whatsapp',
        to,
        type: 'interactive',
        interactive: {
          type: 'button',
          body: { text: body },
          action: {
            buttons: buttons.map(btn => ({
              type: 'reply',
              reply: { id: btn.id, title: btn.title }
            }))
          }
        }
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.WHATSAPP_ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
  }

  // Mark message as read
  static async markRead(messageId: string): Promise<void> {
    await axios.post(
      `${WA_API}/${process.env.WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: 'whatsapp',
        status: 'read',
        message_id: messageId
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.WHATSAPP_ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
  }

  // Send typing indicator (read receipt acts as typing indicator in WA)
  static async sendTyping(to: string): Promise<void> {
    // WhatsApp doesn't have a native typing indicator via API
    // Best practice: mark read immediately, then reply after LLM response
    console.log(`Sending typing indicator to ${to}`);
  }
}
```

---

## 7. Building Your AI Employee Agent

### 7.1 Agent Configuration

```typescript
// agents/employee.agent.ts

import { OpenClawAgent, AgentConfig, Message } from '@openclaw/sdk';
import { tools } from '../tools';
import { memory } from '../memory/store';
import { WhatsAppSender } from '../utils/whatsapp.sender';

const agentConfig: AgentConfig = {
  name: process.env.AGENT_NAME || 'Alex',
  role: process.env.AGENT_ROLE || 'AI Customer Support Specialist',
  company: process.env.AGENT_COMPANY || 'Acme Corp',

  llm: {
    provider: process.env.LLM_PROVIDER as 'openai' | 'anthropic' | 'gemini',
    model: process.env.OPENAI_MODEL || 'gpt-4o',
    temperature: parseFloat(process.env.AGENT_TEMPERATURE || '0.3'),
    maxTokens: parseInt(process.env.AGENT_MAX_TOKENS || '4096'),
  },

  systemPrompt: `
You are ${process.env.AGENT_NAME}, a professional AI Employee working as a 
${process.env.AGENT_ROLE} for ${process.env.AGENT_COMPANY}.

## Your Responsibilities
- Answer customer questions accurately and helpfully
- Schedule appointments and manage calendar requests
- Create and update support tickets
- Escalate complex issues to human agents when needed
- Follow up on open issues proactively

## Your Personality
- Professional yet friendly and warm
- Clear and concise — avoid overly long responses on WhatsApp
- Proactive — offer relevant next steps without being asked
- Honest — if you don't know something, say so and offer to find out

## Response Guidelines for WhatsApp
- Keep messages under 300 characters when possible
- Use line breaks to improve readability
- Use emojis sparingly and professionally ✅
- For complex info, break into multiple short messages
- Always end with a clear next step or question

## Escalation Rules
- If customer is angry or frustrated: empathize first, then escalate if unresolved
- If you cannot find information after 2 attempts: escalate to human
- If customer explicitly asks for a human: immediately escalate
- If legal/financial/medical questions: escalate immediately

## Current Date & Time: ${new Date().toLocaleString('en-US', { timeZone: process.env.AGENT_TIMEZONE })}
`,

  memory: {
    enabled: true,
    store: 'redis',
    ttl: parseInt(process.env.REDIS_SESSION_TTL || '86400'),
    maxMessages: 50,                 // Keep last 50 messages in context
  },

  tools: tools,

  escalation: {
    enabled: true,
    threshold: parseFloat(process.env.AGENT_ESCALATION_THRESHOLD || '0.4'),
    notificationChannel: 'slack',
    humanAgentWebhook: process.env.HUMAN_AGENT_WEBHOOK_URL,
  }
};

export const agent = new OpenClawAgent(agentConfig);

// Main message handler
export async function handleIncomingMessage(
  userId: string,
  content: string,
  channel: 'whatsapp' | 'slack' | 'web'
) {
  try {
    // Mark as read immediately
    if (channel === 'whatsapp') {
      // (message ID would come from webhook context)
    }

    // Load user session from Redis
    const session = await memory.getSession(userId);

    // Run the agent
    const response = await agent.run({
      userId,
      input: content,
      history: session.history,
      context: {
        channel,
        userProfile: session.userProfile,
        timezone: process.env.AGENT_TIMEZONE,
      }
    });

    // Save updated session
    await memory.saveSession(userId, {
      ...session,
      history: response.updatedHistory,
    });

    // Send response back via appropriate channel
    if (channel === 'whatsapp') {
      // Split long responses into multiple messages
      const chunks = splitIntoChunks(response.content, 1000);
      for (const chunk of chunks) {
        await WhatsAppSender.sendText(userId, chunk);
        if (chunks.length > 1) await sleep(500); // slight delay between chunks
      }

      // Offer quick reply buttons if suggestions provided
      if (response.suggestedReplies?.length) {
        await WhatsAppSender.sendButtons(
          userId,
          'Quick options:',
          response.suggestedReplies.slice(0, 3).map((r, i) => ({
            id: `reply_${i}`,
            title: r.substring(0, 20)             // WA button title max 20 chars
          }))
        );
      }
    }

    return response;

  } catch (error) {
    console.error(`Agent error for user ${userId}:`, error);
    if (channel === 'whatsapp') {
      await WhatsAppSender.sendText(
        userId,
        "I'm sorry, I ran into an issue. A human agent will assist you shortly. 🙏"
      );
    }
  }
}

// Helper: split long text
function splitIntoChunks(text: string, maxLength: number): string[] {
  if (text.length <= maxLength) return [text];
  const words = text.split(' ');
  const chunks: string[] = [];
  let current = '';
  for (const word of words) {
    if ((current + word).length > maxLength) {
      chunks.push(current.trim());
      current = '';
    }
    current += word + ' ';
  }
  if (current.trim()) chunks.push(current.trim());
  return chunks;
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### 7.2 Memory Store

```typescript
// memory/store.ts

import { createClient } from 'redis';
import { Pool } from 'pg';

const redis = createClient({ url: process.env.REDIS_URL });
const pg = new Pool({ connectionString: process.env.DATABASE_URL });

redis.connect();

export interface UserSession {
  userId: string;
  history: { role: 'user' | 'assistant'; content: string; timestamp: Date }[];
  userProfile: {
    name?: string;
    email?: string;
    phone?: string;
    company?: string;
    language?: string;
    tags?: string[];
  };
  createdAt: Date;
  lastActivity: Date;
}

export const memory = {

  async getSession(userId: string): Promise<UserSession> {
    const raw = await redis.get(`session:${userId}`);
    if (raw) return JSON.parse(raw);

    // New session
    return {
      userId,
      history: [],
      userProfile: {},
      createdAt: new Date(),
      lastActivity: new Date(),
    };
  },

  async saveSession(userId: string, session: UserSession): Promise<void> {
    session.lastActivity = new Date();
    await redis.setEx(
      `session:${userId}`,
      parseInt(process.env.REDIS_SESSION_TTL || '86400'),
      JSON.stringify(session)
    );
  },

  async clearSession(userId: string): Promise<void> {
    await redis.del(`session:${userId}`);
  },

  // Persist long-term conversation to PostgreSQL
  async archiveConversation(userId: string, session: UserSession): Promise<void> {
    await pg.query(
      `INSERT INTO conversations (user_id, messages, created_at, last_activity)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (user_id) DO UPDATE SET messages = $2, last_activity = $4`,
      [userId, JSON.stringify(session.history), session.createdAt, session.lastActivity]
    );
  }
};
```

---

## 8. Tool & Skill Configuration

### 8.1 Define Agent Tools

```typescript
// tools/index.ts

import { Tool } from '@openclaw/sdk';
import { google } from 'googleapis';

export const tools: Tool[] = [

  // ── Calendar Tool ────────────────────────────────────────
  {
    name: 'check_calendar_availability',
    description: 'Check available time slots in the calendar for a given date range',
    parameters: {
      type: 'object',
      properties: {
        date: { type: 'string', description: 'Date in YYYY-MM-DD format' },
        duration_minutes: { type: 'number', description: 'Meeting duration in minutes' }
      },
      required: ['date']
    },
    execute: async ({ date, duration_minutes = 30 }) => {
      // Integrate with Google Calendar API
      // ... implementation
      return { available_slots: ['10:00 AM', '2:00 PM', '4:30 PM'] };
    }
  },

  // ── CRM Tool ─────────────────────────────────────────────
  {
    name: 'create_support_ticket',
    description: 'Create a new support ticket for a customer issue',
    parameters: {
      type: 'object',
      properties: {
        title: { type: 'string', description: 'Brief issue title' },
        description: { type: 'string', description: 'Detailed issue description' },
        priority: { type: 'string', enum: ['low', 'medium', 'high', 'urgent'] },
        customer_phone: { type: 'string', description: 'Customer WhatsApp number' }
      },
      required: ['title', 'description']
    },
    execute: async ({ title, description, priority = 'medium', customer_phone }) => {
      // Create ticket in your CRM (Zendesk, Freshdesk, etc.)
      const ticketId = `TKT-${Date.now()}`;
      console.log(`Creating ticket: ${ticketId}`);
      return { ticket_id: ticketId, status: 'created', estimated_response: '2-4 hours' };
    }
  },

  // ── Knowledge Base Tool ───────────────────────────────────
  {
    name: 'search_knowledge_base',
    description: 'Search the company knowledge base for information about products or policies',
    parameters: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' },
        category: { type: 'string', description: 'Category to filter by (optional)' }
      },
      required: ['query']
    },
    execute: async ({ query, category }) => {
      // Search your vector DB (Pinecone, Weaviate, pgvector)
      // ... RAG implementation
      return {
        results: [
          { title: 'Return Policy', content: 'We accept returns within 30 days...' },
          { title: 'Shipping Info', content: 'Standard shipping takes 3-5 business days...' }
        ]
      };
    }
  },

  // ── Escalation Tool ───────────────────────────────────────
  {
    name: 'escalate_to_human',
    description: 'Escalate the conversation to a human agent',
    parameters: {
      type: 'object',
      properties: {
        reason: { type: 'string', description: 'Reason for escalation' },
        priority: { type: 'string', enum: ['low', 'medium', 'high', 'urgent'] },
        summary: { type: 'string', description: 'Brief conversation summary' }
      },
      required: ['reason']
    },
    execute: async ({ reason, priority, summary }) => {
      // Notify human agent via Slack/email
      console.log(`Escalating: ${reason} (${priority})`);
      return {
        escalated: true,
        message: "I've connected you with a human agent. They'll be with you shortly! 👋"
      };
    }
  },

  // ── Order Lookup Tool ─────────────────────────────────────
  {
    name: 'lookup_order',
    description: 'Look up order status and details by order ID or phone number',
    parameters: {
      type: 'object',
      properties: {
        order_id: { type: 'string', description: 'Order ID' },
        phone: { type: 'string', description: 'Customer phone number' }
      }
    },
    execute: async ({ order_id, phone }) => {
      // Query your order management system
      return {
        order_id: order_id || 'ORD-123',
        status: 'shipped',
        estimated_delivery: '2025-04-12',
        tracking_number: 'TRK987654321'
      };
    }
  }
];
```

---

## 9. Workflow Automation (Agentic Pipelines)

### 9.1 Multi-Step Workflow with LangGraph

```python
# workflows/support_workflow.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import os

class SupportState(TypedDict):
    user_id: str
    message: str
    intent: Optional[str]
    ticket_id: Optional[str]
    resolution: Optional[str]
    escalated: bool

def classify_intent(state: SupportState) -> SupportState:
    """Classify user intent using LLM"""
    # ... call OpenAI to classify: complaint, question, order_status, etc.
    state['intent'] = 'order_status'
    return state

def handle_order_status(state: SupportState) -> SupportState:
    """Fetch order status"""
    # ... query order system
    state['resolution'] = "Your order #123 is out for delivery today!"
    return state

def handle_complaint(state: SupportState) -> SupportState:
    """Handle customer complaint"""
    state['escalated'] = True
    return state

def should_escalate(state: SupportState) -> str:
    if state.get('escalated'):
        return 'escalate'
    return 'respond'

# Build the graph
workflow = StateGraph(SupportState)
workflow.add_node('classify', classify_intent)
workflow.add_node('handle_order', handle_order_status)
workflow.add_node('handle_complaint', handle_complaint)

workflow.set_entry_point('classify')
workflow.add_conditional_edges(
    'classify',
    lambda s: s['intent'],
    {
        'order_status': 'handle_order',
        'complaint': 'handle_complaint',
    }
)
workflow.add_edge('handle_order', END)
workflow.add_edge('handle_complaint', END)

app = workflow.compile()
```

### 9.2 Scheduled Tasks (Proactive AI Employee)

```typescript
// workflows/scheduled.ts
// Proactive outreach — AI Employee sends follow-ups without waiting for user

import cron from 'node-cron';
import { WhatsAppSender } from '../utils/whatsapp.sender';
import { memory } from '../memory/store';

// Follow up with users who have open tickets — runs every morning at 9 AM PKT
cron.schedule('0 9 * * *', async () => {
  console.log('Running morning follow-up task...');

  const openTickets = await getOpenTickets();  // from your CRM

  for (const ticket of openTickets) {
    const session = await memory.getSession(ticket.customerPhone);

    if (isStale(session, 24 * 60 * 60)) {  // 24h since last interaction
      await WhatsAppSender.sendText(
        ticket.customerPhone,
        `Hi ${session.userProfile.name || 'there'}! 👋 Following up on ticket #${ticket.id} — our team is still working on it. Expected resolution: ${ticket.eta}. Reply if you have questions!`
      );
    }
  }
}, { timezone: process.env.AGENT_TIMEZONE });

function isStale(session: any, thresholdSeconds: number): boolean {
  const lastActivity = new Date(session.lastActivity).getTime();
  return (Date.now() - lastActivity) > thresholdSeconds * 1000;
}
```

---

## 10. Deployment & Scaling

### 10.1 Production Docker Setup

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

```yaml
# docker-compose.prod.yml
version: '3.9'

services:
  openclaw-app:
    build: .
    container_name: openclaw-ai-employee
    ports:
      - "3000:3000"
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: openclaw
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: openclaw_db
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - openclaw-app
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### 10.2 Deploy to Kubernetes

```bash
# Build and push Docker image
docker build -t your-registry/openclaw-ai-employee:latest .
docker push your-registry/openclaw-ai-employee:latest

# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Verify
kubectl get pods -n openclaw
kubectl logs -f deployment/openclaw-ai-employee -n openclaw
```

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openclaw-ai-employee
  namespace: openclaw
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openclaw-ai-employee
  template:
    metadata:
      labels:
        app: openclaw-ai-employee
    spec:
      containers:
        - name: openclaw
          image: your-registry/openclaw-ai-employee:latest
          ports:
            - containerPort: 3000
          envFrom:
            - secretRef:
                name: openclaw-secrets
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 15
            periodSeconds: 20
```

### 10.3 Horizontal Scaling

```bash
# Scale up replicas manually
kubectl scale deployment openclaw-ai-employee --replicas=5 -n openclaw

# Or set up HorizontalPodAutoscaler
kubectl autoscale deployment openclaw-ai-employee \
  --cpu-percent=70 --min=2 --max=10 -n openclaw
```

---

## 11. Monitoring & Observability

### 11.1 Health Check Endpoint

```typescript
// src/routes/health.ts
import { Router } from 'express';
import { redis } from '../memory/store';

const router = Router();

router.get('/health', async (req, res) => {
  const checks = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    redis: 'unknown',
    database: 'unknown',
    whatsapp_api: 'unknown',
  };

  try {
    await redis.ping();
    checks.redis = 'connected';
  } catch { checks.redis = 'error'; }

  res.status(200).json(checks);
});

export default router;
```

### 11.2 Key Metrics to Track

```typescript
// metrics to log and monitor
const metrics = {
  messages_received_total: 0,
  messages_sent_total: 0,
  agent_response_time_ms: [],
  escalations_total: 0,
  tool_calls_total: {},
  active_sessions: 0,
  llm_tokens_used: 0,
  errors_total: 0,
};

// Example: log to console / send to Datadog / Prometheus
function recordMetric(name: string, value: number) {
  console.log(JSON.stringify({ metric: name, value, timestamp: Date.now() }));
}
```

### 11.3 Useful Log Queries

```bash
# View live agent logs
docker logs -f openclaw-ai-employee

# Filter escalations only
docker logs openclaw-ai-employee 2>&1 | grep "ESCALAT"

# Monitor response times
docker logs openclaw-ai-employee 2>&1 | grep "response_time"

# Kubernetes logs
kubectl logs -f deployment/openclaw-ai-employee -n openclaw --tail=100
```

---

## 12. Security & Compliance

### 12.1 Webhook Signature Verification

```typescript
// Always verify WhatsApp webhook signatures in production
import crypto from 'crypto';

function verifyWebhookSignature(
  payload: string,
  signature: string,
  appSecret: string
): boolean {
  const expected = crypto
    .createHmac('sha256', appSecret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(`sha256=${expected}`),
    Buffer.from(signature)
  );
}

// Use in webhook middleware:
app.use('/webhooks/whatsapp', (req, res, next) => {
  const sig = req.headers['x-hub-signature-256'] as string;
  const raw = (req as any).rawBody;

  if (!verifyWebhookSignature(raw, sig, process.env.META_APP_SECRET!)) {
    return res.status(401).send('Invalid signature');
  }
  next();
});
```

### 12.2 Data Privacy Best Practices

```bash
# Never log full message content in production
# Use PII masking:
function maskPII(text: string): string {
  return text
    .replace(/\+?[0-9]{10,15}/g, '[PHONE]')
    .replace(/[\w.-]+@[\w.-]+\.\w+/g, '[EMAIL]')
    .replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[CARD]');
}

# Set session expiry — no indefinite data retention
REDIS_SESSION_TTL=86400   # 24 hours

# Encrypt sensitive data at rest
# Use Postgres column-level encryption for userProfile fields
```

### 12.3 Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

// Protect webhook endpoint
const webhookLimiter = rateLimit({
  windowMs: 60 * 1000,        // 1 minute
  max: 500,                    // WhatsApp can send bursts
  message: 'Too many requests',
});

app.use('/webhooks/whatsapp', webhookLimiter);
```

---

## 13. Troubleshooting

### Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Webhook not receiving messages | No POST requests from Meta | Check HTTPS cert is valid; verify webhook in Meta console |
| 401 Unauthorized | `Invalid OAuth access token` | Regenerate access token in Meta Developer Console |
| Message not delivered | No error but user doesn't receive | Check phone number format (must include country code, no `+`) |
| Session not persisting | Agent forgets context | Check Redis is running: `docker ps` and `redis-cli ping` |
| Agent response too slow | User times out | Check LLM API latency; implement streaming responses |
| Webhook verify fails | Meta shows "Verification failed" | Ensure `WHATSAPP_WEBHOOK_VERIFY_TOKEN` matches exactly |
| Docker OOM | Container killed | Increase memory limits in docker-compose or K8s resources |

### Debug Commands

```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping
# Expected: PONG

# Test WhatsApp API token
curl -s "https://graph.facebook.com/v20.0/me?access_token=$WHATSAPP_ACCESS_TOKEN" | jq .

# Check webhook subscription status
curl -s "https://graph.facebook.com/v20.0/$WHATSAPP_BUSINESS_ACCOUNT_ID/subscribed_apps" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" | jq .

# Test local webhook with ngrok
ngrok http 3000 --log stdout

# Validate .env loaded correctly
node -e "require('dotenv').config(); console.log(process.env.WHATSAPP_PHONE_NUMBER_ID)"

# View PostgreSQL conversation logs
psql $DATABASE_URL -c "SELECT user_id, last_activity FROM conversations ORDER BY last_activity DESC LIMIT 10;"
```

---

## 14. Reference: Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENCLAW_PORT` | Yes | App server port (default: 3000) |
| `OPENCLAW_SECRET` | Yes | App secret for internal signing |
| `LLM_PROVIDER` | Yes | `openai` \| `anthropic` \| `gemini` |
| `OPENAI_API_KEY` | Yes* | OpenAI API key |
| `ANTHROPIC_API_KEY` | No | Anthropic API key (fallback) |
| `WHATSAPP_PHONE_NUMBER_ID` | Yes | From Meta Developer Console |
| `WHATSAPP_ACCESS_TOKEN` | Yes | Permanent system user token |
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | Yes | Custom string you define |
| `META_APP_SECRET` | Yes | For webhook signature verification |
| `REDIS_URL` | Yes | Redis connection string |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `AGENT_NAME` | No | AI Employee name (default: Alex) |
| `AGENT_ROLE` | No | Role/job title of the AI Employee |
| `AGENT_COMPANY` | No | Company name shown in responses |
| `AGENT_TIMEZONE` | No | Timezone for date-aware responses |
| `AGENT_ESCALATION_THRESHOLD` | No | Confidence threshold for escalation (0.0–1.0) |
| `PUBLIC_URL` | Yes | HTTPS public URL for webhooks |

---

## Quick Start Summary

```bash
# 1. Clone & install
git clone https://github.com/openclaw-ai/openclaw.git && cd openclaw
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with your keys

# 3. Start infrastructure
docker compose up -d redis postgres

# 4. Set up WhatsApp webhook
ngrok http 3000  # copy HTTPS URL → Meta Developer Console

# 5. Start the AI Employee
npm run dev

# 6. Send a WhatsApp message to your test number
# Your AI Employee is live! 🤖
```

---

*Guide Version 1.0 | Last updated: April 2026*  
*Built for OpenClaw + WhatsApp Business API (Meta Graph API v20.0)*
