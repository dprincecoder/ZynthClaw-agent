# ZynthClaw — Cursor conversation summary (for submission)

**What this document is**

This is a **condensed summary produced in Cursor** so it can be attached to hackathon / Synthesis submissions. The **full agent–human conversation** that built and iterated on ZynthClaw spans **multiple Cursor sessions** and a large export (`conversation_formatted.md` derived from `conversation.jsonl`, **~130KB+** and **thousands of lines**), which is **impractical to submit in full**. This file captures the **substance** of that work: requirements, major decisions, and outcomes.

---

## One-line pitch

**ZynthClaw** is a **Telegram-first Public Goods Evaluation Agent** for **Digital Public Infrastructure (DPI)**: it collects **X (Twitter) signals**, **human impact stories**, optional **GitHub activity**, optional **extra context**, and **governance** inputs, then produces an **Impact Evaluation Report**, **mechanism design** guidance, and a **raw-data PDF** export (`/export` or `POST /export`).

---

## Evolution of the product

1. **From “funding / infra risk” to public goods**  
   Early work focused on topic/repo scans and funding-style flows. The product was **refocused** on a **staged conversational evaluation**: no funding-candidate pipeline; emphasis on **community sentiment**, **user impact**, **developer signals**, and **mechanism design** for public-goods funding decisions.

2. **Telegram UX**  
   - Commands: `/start`, `/evaluate_project`, `/export`.  
   - Flow: **X handle** → **bio** + **3-post preview** (nested replies) → **long-form impact feedback** (minimum substance enforced) → optional **GitHub repo** → optional **additional info** → **governance** Q&A (how decisions work; links/artifacts) → **status lines** (“Analysing social / developer / governance activity”) → **report**.  
   - **PDF export** of raw threaded data (no email; SendGrid/SMTP removed for Railway constraints).  
   - **LLM roadmap (beta)** called out in `/start`, README, skill, and homepage.

3. **X (Twitter) integration**  
   Migrated from scraping ideas to **official X API v2** in `twitter_scraper.py`: user bio, original posts, replies via **`conversation_id`** search, filtering (e.g. link-only replies), caps/timeouts for production stability.  
   Previews and PDFs include **threaded posts + replies**.

4. **Evaluation engine**  
   `public_evaluator.py`: **XSignals**, **GitHubSignals** via existing **Evaluator** / **GitHubService**, **impact classification** (High / Moderate / Emerging), **mechanism design** narrative; extended with **governance** fields and PDF blocks.

5. **API & export**  
   - **FastAPI**: homepage, `GET /skill.md`, **`GET /export`** (help JSON), **`POST /export`** (JSON evaluation → PDF).  
   - Legacy **topic/repo HTTP APIs** and **crawler/funding** code removed; **`core/`** removed.

6. **Docs & deployment**  
   **README**, **skill.md**, homepage aligned with the new flow. **Docker** / **Railway** deployment; **GitHub** `ZynthClaw-agent`; **Moltbook** registration/posts; **Synthesis** project draft and metadata updates.

7. **Ops / quality**  
   Production **timeouts** addressed by capping X fetch scope and tightening HTTP timeouts. **DMARC / email** issues led to **dropping email** in favor of **Telegram + HTTP PDF**.

---

## Technical stack (high level)

- **Python**, **FastAPI**, **python-telegram-bot**, **httpx** / **requests**, **ReportLab** (PDF).  
- **X API v2**, **GitHub API**, **Railway** hosting.

---

## Outcome

A **modular** codebase with clear separation: **X layer**, **GitHub layer**, **Telegram orchestration**, **public evaluator**, **PDF generation**, and **HTTP export** for other AI agents—documented for humans (`README`, `skill.md`) and for programmatic PDF download (`POST /export`).

---

*End of Cursor submission summary.*
