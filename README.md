# VyapaarMitra — Voice Agent for Local Commerce

**VyapaarMitra** is an interactive, multilingual voice agent built for the Local Commerce track of Murf AI's "10 Days of AI Voice Agents" challenge. It enables customers to directly call a local shop and talk to an AI agent to search catalogues, check prices/stock, and place/confirm orders in real-time, completely replacing the need to browse complex WhatsApp catalogues or navigate tedious websites.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Murf Falcon](https://img.shields.io/badge/TTS-Murf%20Falcon-6366F1)](https://murf.ai/api/docs/text-to-speech/streaming) [![LiveKit](https://img.shields.io/badge/Transport-LiveKit-002cf2)](https://docs.livekit.io) [![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/) [![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

---

## What It Does

- 🗣️ **Multilingual & Code-Mixed Conversations:** Talks fluently to callers in Telugu, Hindi, English, and natural code-mixed vernacular (like Hinglish or Telglish).
- 📦 **Live Catalogue Search:** Accesses a live local store database to instantly check item prices, stock availability, and buyer ratings.
- 🧠 **Smart Caller Memory:** Remembers returning callers and greets them warmly by name, strictly adhering to the user's explicit consent before storing any data.
- 🚨 **Instant Human Escalation:** Automatically alerts human shop owners via a formatted Discord webhook notification for order confirmations, returns, or complex out-of-scope inquiries.
- 📞 **Outbound Order Confirmations:** Proactively places outbound telephone calls to buyers to verbally verify order placement and details.
- 🔄 **Returns & Refunds Specialist:** Seamlessly hands off return/refund queries to a dedicated specialist agent, which activates a distinct voice and updates the frontend UI styling to match.

---

## Tech Stack

- **STT (Speech-to-Text):** [Deepgram](https://deepgram.com) (using the advanced `nova-3` multilingual model)
- **LLM (Large Language Model):** [Gemini](https://aistudio.google.com/) (for low-latency, highly intelligent context processing)
- **TTS (Text-to-Speech):** [Murf Falcon](https://murf.ai/falcon) — the fastest production TTS API. Features **Anisha** (Indian English, Female) for the main store assistant, and **Samar** (Indian English, Male) for the Returns & Refunds specialist.
- **Real-time Transport:** [LiveKit](https://livekit.io/) (including full LiveKit SIP/telephony support for answering standard phone calls)
- **Frontend:** [Next.js](https://nextjs.org/) (React, TypeScript, TailwindCSS, custom audio visualizers, and state-driven UI themes)
- **Storage:** [SQLite](https://sqlite.org/) (for managing local session records, caller memory, and the inventory catalogue)

---

## Why Murf Falcon

- **55ms model latency** - fastest production TTS
- **130ms time-to-first-audio** across 10+ global regions
- **$0.01/1000 characters** - up to 10x cheaper than alternatives
- **150+ voices** across 35+ languages
- **99.38% pronunciation accuracy**

---

## Architecture

```mermaid
flowchart LR
    A[🎙️ User speaks] -->|audio| B[Deepgram STT]
    B -->|text| C[LLM]
    C -->|response text| D[Murf Falcon TTS]
    D -->|audio| E[LiveKit]
    E -->|stream| F[🔊 User hears]

    style A fill:#444441,stroke:#888780,color:#fff
    style B fill:#185FA5,stroke:#85B7EB,color:#fff
    style C fill:#534AB7,stroke:#AFA9EC,color:#fff
    style D fill:#0F6E56,stroke:#5DCAA5,color:#fff
    style E fill:#D85A30,stroke:#F0997B,color:#fff
    style F fill:#444441,stroke:#888780,color:#fff
```

---

## Quickstart

### Prerequisites

- **Python** 3.10+
- **[uv](https://docs.astral.sh/uv/)** - fast Python package manager
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Node.js** 18+
- **pnpm** — fast Node package manager
  ```bash
  npm install -g pnpm
  ```
- A [LiveKit](https://cloud.livekit.io/) project (free tier available)

### Step 1: Clone the repo

```bash
git clone https://github.com/murf-ai/murf-livekit-starter.git
cd murf-livekit-starter
```

### Step 2: Set up environment variables

To run the application, you must set up environment variables for both the backend and frontend.

1. Create a `.env.local` file inside the `backend/` directory.
2. Create a `.env.local` file inside the `frontend/` directory.

**Crucial Security Warning:** These `.env.local` files are configured in `.gitignore` and **must never be committed** to source control. Never place real, active API keys in your `README.md` or template files.

#### Backend Environment Variables (`backend/.env.local`)

| Variable | Source / Description | Required |
|---|---|---|
| `LIVEKIT_URL` | LiveKit Cloud dashboard (your project settings) | Yes |
| `LIVEKIT_API_KEY` | LiveKit Cloud dashboard (your project settings) | Yes |
| `LIVEKIT_API_SECRET` | LiveKit Cloud dashboard (your project settings) | Yes |
| `MURF_API_KEY` | [Murf API Dashboard](https://murf.ai/api/dashboard) | Yes |
| `DEEPGRAM_API_KEY` | [Deepgram Console](https://deepgram.com) | Yes |
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/) (for Gemini model) | Yes |
| `DISCORD_WEBHOOK_URL` | Discord Channel settings → Integrations → Webhooks (for human escalations) | Yes |

#### Frontend Environment Variables (`frontend/.env.local`)

| Variable | Source / Description | Required |
|---|---|---|
| `LIVEKIT_URL` | LiveKit Cloud URL | Yes |
| `LIVEKIT_API_KEY` | LiveKit API Key | Yes |
| `LIVEKIT_API_SECRET` | LiveKit API Secret | Yes |
| `AGENT_NAME` | Set to `my-agent` or leave blank for automatic dispatch | Optional |

### Step 3: Install backend dependencies

```bash
cd backend
uv sync
uv run python src/agent.py download-files
```

### Step 4: Install frontend dependencies

```bash
cd frontend
pnpm install
```

### Step 5: Run the application

**Option A - All-in-one (from repo root):**

```bash
# macOS/Linux
chmod +x start_app.sh
./start_app.sh

# Windows (PowerShell)
.\start_app.ps1
```

**Option B - Separate terminals:**

```bash
# Terminal 1 — LiveKit Server (if running locally)
livekit-server --dev

# Terminal 2 — Backend agent
cd backend && uv run python src/agent.py dev

# Terminal 3 — Frontend
cd frontend && pnpm dev
```

Then open **http://localhost:3000** in your browser.

---

## Testing a Conversation

### Testing via the Web Browser

1. Open **http://localhost:3000** in your web browser.
2. Ensure both your backend agent and frontend application are running.
3. Click the **Start talking** button in the UI.
4. Allow microphone access when prompted.
5. Speak to the agent (e.g., "Hello, do you have fresh mangoes in stock?"). The agent will reply in real-time, and you'll see live transcriptions, custom visualizers, and state indicators on-screen.

### Testing via a Telephone Call (SIP / VoIP)

To test the agent over an actual phone call using SIP:
1. Configure a SIP trunk/inbound number in your LiveKit Cloud account under the **Telephony (SIP)** tab.
2. Ensure your backend python agent is running (`uv run python src/agent.py dev`).
3. Use a softphone client like **Linphone** (or another SIP-compatible dialer/actual phone) to place a VoIP call to your LiveKit SIP URI or telephone number.
4. The backend agent will receive the inbound call, detect the SIP participant channel, automatically activate standard telephony-optimized noise cancellation, and greet you verbally.
5. Talk to the agent just like a standard phone call.

---

## Deploy

Want to deploy this beyond localhost? You'll need to deploy **two services**: the backend agent and the frontend. Both must use the same LiveKit project.

> This is a two-service app — the backend agent and the frontend UI deploy separately. You'll need both running and connected to the same LiveKit project.

### Backend (Python agent) — Deploy to Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/tIVCF1?referralCode=cNjn2P&utm_medium=integration&utm_source=template&utm_campaign=generic)

Set these environment variables in Railway:

- `MURF_API_KEY`
- `DEEPGRAM_API_KEY`
- `GOOGLE_API_KEY`
- `DISCORD_WEBHOOK_URL`
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`

The backend runs as a long-lived Python process that connects to LiveKit as an agent. Railway handles this well.

### Frontend (Next.js) — Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/murf-ai/murf-livekit-starter&root-directory=frontend&env=LIVEKIT_URL,LIVEKIT_API_KEY,LIVEKIT_API_SECRET&project-name=murf-voice-agent&repository-name=murf-voice-agent)

Set these environment variables in Vercel:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `AGENT_NAME` (optional — for explicit agent dispatch)

The frontend is a standard Next.js app. Point it at the same LiveKit instance your backend agent is connected to.

### Connecting them

The frontend and backend don't call each other directly — they both connect to **LiveKit**, which handles the real-time audio transport.

1. Use the **same** `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` on both Railway and Vercel
2. Set `AGENT_NAME=my-agent` on Vercel — this matches the `agent_name="my-agent"` registered in `backend/src/agent.py`
3. Verify: Railway logs should show the agent connected to LiveKit. Open your Vercel URL, click **Start talking** — the agent should respond

If the agent doesn't connect, double-check that both services point to the same LiveKit project and that the backend is running (check Railway logs).

---

## Change the Use Case

The default system prompt makes this a **customer support agent**. You can change the agent’s behavior by editing the prompt.

**Where the prompt lives:** `backend/src/agent.py`- the `SYSTEM_PROMPT` constant (near the top of the file, after the imports). Change that string to change what your voice agent does.

### Example prompts (copy-paste)

**Customer Support (default):**

```
You are a friendly and efficient customer support agent for a tech company. Help users with account issues, billing questions, and product troubleshooting. Be concise, empathetic, and solution-oriented. If you don't know something, say so honestly and offer to escalate.
```

**Language Tutor:**

```
You are a patient and encouraging language tutor helping the user practice conversational Spanish. Speak primarily in Spanish but switch to English to explain grammar or vocabulary when needed. Correct mistakes gently and suggest better phrasing. Keep conversations natural and fun.
```

**AI Receptionist:**

```
You are a professional receptionist for a medical clinic. Help callers schedule appointments, answer questions about office hours and services, and take messages for doctors. Be warm but efficient. Ask for the caller's name and reason for calling upfront.
```

See the Configuration section below for voice, STT, and LLM options.

---

## Configuration

### Murf voice

Edit the `tts=murf.TTS(...)` call in `backend/src/agent.py`. Set the `voice` argument to any Murf voice ID. Examples:

- `Anisha` — Indian English (female, default in this starter)
- `Pooja` — Indian English (female)
- `Samar` — Indian English (male)
- `Amara` — US English (female)
- `Gordon` — US English (male)
- `Hazel` — UK English (female)
- `Bertie` — UK English (male)

Browse all voices: [Murf Voice Library](https://murf.ai/api/docs/voices-styles/voice-library).

### STT provider

STT is configured in `backend/src/agent.py` in the `AgentSession(stt=...)` call. The default is Deepgram (`deepgram.STT(model="nova-3")`). You can swap to another LiveKit-compatible STT plugin if needed.

### LLM (Gemini vs OpenAI)

- **Gemini (default):** Set `GOOGLE_API_KEY` and use `llm=google.LLM(model="gemini-3.5-flash-lite")` in `agent.py`.
- **OpenAI:** Set `OPENAI_API_KEY`, add the OpenAI plugin, and use the corresponding `llm=openai.LLM(...)` in `agent.py`.

### Audio format

Murf Falcon and LiveKit handle audio format internally. For advanced options, see [Murf API docs](https://murf.ai/api/docs) and [LiveKit docs](https://docs.livekit.io).

---

## Project Structure

```
murf-livekit-starter/
├── backend/                 # Python voice agent (LiveKit Agents + Murf Falcon)
│   ├── src/
│   │   └── agent.py         # Agent entrypoint, pipeline (STT/LLM/TTS), system prompt
│   ├── tests/               # Agent tests
│   ├── .env.example         # Backend env template
│   ├── pyproject.toml       # Python deps (uv)
│   └── railway.toml         # Railway deploy config
├── frontend/                # Next.js UI for voice sessions
│   ├── app/
│   │   ├── page.tsx         # Main page
│   │   └── api/token/       # LiveKit token endpoint (dev)
│   ├── components/          # UI (agents-ui, app config, theme)
│   ├── app-config.ts        # Branding, title, button text, accent
│   ├── .env.example         # Frontend env template
│   └── package.json         # Node deps (pnpm)
├── start_app.sh             # Start LiveKit + backend + frontend (macOS/Linux)
├── start_app.ps1            # Start LiveKit + backend + frontend (Windows)
├── README.md                # This file
```

For deeper documentation on each part, see:

- [Backend Documentation](./backend/README.md) — agent pipeline, voice/LLM/STT configuration, testing, deployment
- [Frontend Documentation](./frontend/README.md) — UI customization, visualizers, theming, component architecture

---

## Links

- [Murf API Docs](https://murf.ai/api/docs)
- [Murf Voice Library](https://murf.ai/api/docs/voices-styles/voice-library)
- [LiveKit Docs](https://docs.livekit.io)
- [Deepgram Docs](https://developers.deepgram.com)
- [Murf Falcon Benchmarks](https://murf.ai/falcon/benchmarks)
- [TTS Latency Benchmarker](https://github.com/sahilsgupta/tts-latency-benchmarker) — run your own p50/p95 tests across providers
- [Murf Discord](https://discord.gg/FbKAy96Sz7)
- [Murf Startup Incubator](https://murf.ai/api) — 50M free characters for startups

---

## About This Project

**VyapaarMitra** was built as part of the **10 Days of Voice Agents — #VoiceForBharat Edition** challenge.

[Read the full story](BLOG_LINK_HERE) on how we designed, developed, and deployed this voice agent.

Special thanks to **[Murf Falcon](https://murf.ai/falcon)** for providing the ultra-low-latency, high-fidelity streaming Text-to-Speech API that powers our voices (**Anisha** and **Samar**), making conversational voice interfaces accessible and human-like for local commerce.

---

## License

MIT

---

# 10 Days of Voice Agents — #VoiceForBharat Edition

Welcome to **10 Days of Voice Agents, #VoiceForBharat Edition**, by [murf.ai](https://murf.ai/api)!

## About the Challenge

We built **[Murf Falcon](https://murf.ai/falcon)**, the consistently fastest TTS API — and **[Falcon 2](https://murf.ai/api/docs/text-to-speech-models/falcon-2)**, our latest streaming model, gets you to ~100 ms latency. This August, you're going to use it to build voice agents for the people who need them most.

**Build one voice agent over ten days**, from August 6th to August 15th, ending on Independence Day. The agent gets a new capability every day, until it can answer a real phone call and solve a real problem for someone in India.

### How It Works

- **One task each day**, published here and announced to all participants
- **Pick a track on Day 1** and build for it all ten days
- **Post your progress on LinkedIn every day**, tagging Murf AI and using **#VoiceForBharat**
- **Ship a working, deployed agent by Day 10**

### Why Bharat

Most voice AI gets built for people who already have apps, data plans and English. This challenge is for the rest — the farmer checking a market rate before hiring a truck, the ASHA worker with forty households and no tooling, the family that needs a flood warning tonight.

Voice is the interface that works with **everyone**.

## Tracks

| Track | For |
|---|---|
| **Farm & Field** | Crop advisory, market prices, weather alerts, input costs |
| **Health Access** | Symptom triage, ASHA worker tools, medication reminders, scheme eligibility |
| **Learning & Literacy** | Voice tutoring for children and adult learners, spoken-English practice |
| **Local Commerce** | Order taking and catalogue tools for artisans, MSMEs, street vendors |
| **Financial Services** | Government scheme explainers, banking literacy, fraud awareness |
| **Disaster Response** | Flood and drought alerting, relief coordination, welfare check-ins |

## Quick Start

### Prerequisites

- A **Murf API account** — sign up at the [Murf API dashboard](https://murf.ai/api/dashboard) to get your API key
- Python 3.9+ with [uv](https://docs.astral.sh/uv/)
- [LiveKit Server](https://docs.livekit.io/transport/self-hosting/local/) for local development
- [LiveKit CLI](https://docs.livekit.io/intro/basics/cli/) (optional, recommended)

### Setup

1. **Fork and clone the [starter repository](https://github.com/murf-ai/murf-livekit-starter).**
2. **Install dependencies** and **copy the example environment file**, following the setup instructions in the starter.
3. **Add your API keys.** Create your Murf key from the [Murf API dashboard](https://murf.ai/api/dashboard) — the [quickstart](https://murf.ai/api/docs/introduction/quickstart#generate-an-api-key) walks you through it step by step.
4. **Run the agent** and talk to it.

You're not required to use the starter. Build in whatever language and framework you like — **using Murf Falcon for speech is the only requirement.**

## Daily Challenge Tasks

Each day you'll get a new task that builds on the agent you already have. The tasks are released here in the challenges folder.

**Stay tuned for daily task announcements!**

## Submitting Your Work

Each day:

1. **Build** the day's task in your fork.
2. **Record a short video** showing the specific thing that task asks for.
3. **Post it on LinkedIn**, tagging **Murf AI** and using **#VoiceForBharat**.

Your repo should tell the story by Day 10: a clear README, an honest known-limitations section, and a deployed agent someone can actually reach.

## Documentation & Resources

- [Murf LiveKit Starter](https://github.com/murf-ai/murf-livekit-starter) — the starter repo for this challenge
- [Murf API Dashboard](https://murf.ai/api/dashboard) — sign up and generate your API key
- [Murf API Quickstart](https://murf.ai/api/docs/introduction/quickstart#generate-an-api-key) — how to generate an API key, step by step
- [Murf API Documentation](https://murf.ai/api/docs/introduction/overview)
- [Falcon 2 Model Documentation](https://murf.ai/api/docs/text-to-speech-models/falcon-2)
- [Murf TTS Streaming Guide](https://murf.ai/api/docs/text-to-speech/streaming)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit Telephony](https://docs.livekit.io/telephony/)
- [Backend Template](https://github.com/livekit-examples/agent-starter-python)
- [Frontend Template](https://github.com/livekit-examples/agent-starter-react)
- [LiveKit Agent Examples](https://github.com/livekit-examples/python-agents-examples)
- [Testing Voice Agents](https://docs.livekit.io/agents/start/testing/)

---

**Ten days. One agent. Build something someone can actually use, and have fun while doing it!**

Built for #VoiceForBharat by [murf.ai](https://murf.ai/api)
