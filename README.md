# ZynthClaw (Zyntux) – Open Source Funding Radar

ZynthClaw is an AI agent that finds **critical open-source infrastructure** that may need funding or community support. It crawls GitHub by topic or repository, collects maintenance and ecosystem metrics, and surfaces **funding candidates**—projects with high dependents but few active maintainers.

## Why it exists

Many essential libraries and tools power huge ecosystems but are maintained by very few people. When those maintainers burn out or move on, **whole dependency trees are at risk**. ZynthClaw helps find and prioritize these projects so funders and communities can support them before it’s too late.

---

## Features

- **GitHub crawling by topics** – Search top repositories for given GitHub topics with optional minimum star thresholds.
- **Single-repo evaluation** – Evaluate one repository by URL.
- **Rich metrics** – Stars, forks, open issues, creation date, last commit, total contributors, active contributors (90d), dependents count.
- **Scoring** – `impact_score`, `maintainer_sustainability_score`, `ecosystem_dependency_score`, `criticality_score`, and `risk_flag` (LOW / MEDIUM / HIGH).
- **Funding / risk analysis** – Automatic `analysis` text for fragile backbone projects.
- **REST API** – `POST /evaluate/topics`, `POST /evaluate/repo`, `GET /evaluations`, `GET /skill.md`.
- **Telegram bot** – Chat with ZynthClaw via Telegram: scan topics, analyze repos, get funding targets, request email reports.
- **Email + PDF report** – Send the top funding candidates to any email address as a clean PDF attachment.
- **Homepage** – Human-friendly landing page with what the agent does, why it exists, and how to talk to it (API + Telegram).
- **Agent skill file** – `GET /skill.md` exposes a markdown skill description so other AI agents can discover and use ZynthClaw via curl.

---

## Getting started

### 1. Homepage (once the app is running)

When the API is running, open the **homepage** in your browser:

- **Local:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Deployed:** `https://your-deployed-host/`

There you’ll see:

- What ZynthClaw does
- Why it exists and the problem it solves
- **How to talk to ZynthClaw:**
  1. **AI agents** – Copy the `curl` command to fetch `skill.md`; your agent will know what to do from there.
  2. **Telegram** – Link to start a chat with the ZynthClaw bot (if `TELEGRAM_BOT_USERNAME` is set).

### 2. Run the app

See [Installation](#installation) and [Running](#running) below. Use `run_agent.py` to start both the **API** and the **Telegram bot** together.

---

## Project structure

```text
Zynthclaw/
  app/
    config.py          # Settings (GitHub, SMTP, Telegram)
    main.py            # FastAPI app: homepage, API routes, skill.md
    crawler.py         # GitHub topic crawling
    evaluator.py       # Repo metrics and scoring
    github_service.py  # GitHub API client
    email_service.py   # Email + PDF report delivery
  core/
    agent_controller.py  # Scan topic/repo, get funding targets (used by API + bot)
  tg_bot/
    bot.py            # Telegram handlers and commands
    formatters.py     # Message formatting for Telegram
  run_agent.py        # Entrypoint: starts API + Telegram bot
  skill.md            # Agent skill description (also served at GET /skill.md)
  requirements.txt
  .env                # Secrets (not committed; see .gitignore)
```

---

## Configuration

Create a `.env` file in the project root (see `.env.example` or below). Required for full functionality:

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | GitHub API (higher rate limits; recommended) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (required if you run the bot) |
| `TELEGRAM_BOT_USERNAME` | Bot username for homepage link (e.g. `MyBot` → t.me/MyBot) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` | Email delivery for `/email_targets` |

Example `.env`:

```env
GITHUB_TOKEN=ghp_your_token_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_USERNAME=YourBotUsername
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_FROM_EMAIL=bot@example.com
```

---

## Installation

```bash
cd /path/to/Zynthclaw
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running

**API + Telegram bot together (recommended):**

```bash
python run_agent.py
```

- API: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (homepage, docs, and routes).
- Telegram bot starts polling; use your bot in Telegram as configured.

**API only (e.g. for development):**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) for the homepage and [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger.

---

## How to talk to ZynthClaw

### 1. Homepage and AI agents

- Open the **homepage** (`/`) for a short description and two options:
  - **curl to skill file** – e.g. `curl -s "https://your-host/skill.md"` so another AI agent can read the skill and call the API.
  - **Telegram** – link to open a chat with the bot (if `TELEGRAM_BOT_USERNAME` is set).

### 2. Telegram integration

In Telegram, send:

| Command | Description |
|--------|-------------|
| `/start` | Intro and list of commands |
| `/scan <topic>` | Crawl GitHub for a topic and return funding candidates (e.g. `/scan ethereum`) |
| `/scan` | Bot asks you to send a topic in the next message |
| `/repo <github_url>` | Evaluate one repository |
| `/repo` | Bot asks you to send the repo URL in the next message |
| `/funding_targets` | Return the latest cached funding targets from the last scan/repo run |
| `/email_targets` | Send the latest funding targets to an email as a PDF |
| `/email_targets <email>` | Same, with email in the command; or send email in the next message if you use `/email_targets` alone |

The bot replaces its last status message with the result (e.g. “Scanning…” then the actual reply).

### 3. REST API

- **Evaluate by topics:** `POST /evaluate/topics` with `{"topics": ["topic1", "topic2"], "min_stars": 100}`  
- **Evaluate one repo:** `POST /evaluate/repo` with `{"repo_url": "https://github.com/owner/repo"}`  
- **Last evaluation results:** `GET /evaluations`  
- **Agent skill (for other AI agents):** `GET /skill.md`

---

## REST API quick reference

### Evaluate by topics

`POST /evaluate/topics`

```json
{
  "topics": ["ethereum", "wallet"],
  "min_stars": 100
}
```

Returns funding candidates (and updates the cache used by `/funding_targets` and `/email_targets`).

### Evaluate a single repository

`POST /evaluate/repo`

```json
{
  "repo_url": "https://github.com/owner/repo"
}
```

### Get last evaluation results

`GET /evaluations` – Returns the most recent funding candidates and full evaluations from the last topic or repo run.

### Get agent skill (for AI agents)

`GET /skill.md` – Markdown description of what ZynthClaw does and how to call it (endpoints, request/response shapes). Use this so other agents can integrate via the API.

---

## Email report (PDF)

When you use **Telegram** `/email_targets` (with or without an email in the command), the bot:

1. Uses the latest funding targets (from the last `/scan`, `/repo`, or `/funding_targets`).
2. Asks for an email if you didn’t provide one.
3. Builds a clean email with a **PDF attachment** of the top funding candidates and sends it via SMTP.

Requires SMTP env vars to be set; see [Configuration](#configuration).

---

## License and credits

See the **footer on the homepage** for credits. ZynthClaw was made for the **Octant hackathon** in partnership with **Synthesis**.
