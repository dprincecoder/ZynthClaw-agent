# Zyntux – AI Evaluation Agent

Zyntux is an AI agent that evaluates open-source GitHub repositories based on their activity, ecosystem, dependencies, contributors, funding impact, and maintenance signals.

## Features

- **GitHub crawling by topics**: Search top repositories for given GitHub topics with optional minimum star thresholds.
- **Repository metrics collection**: Stars, forks, open issues, creation date, last commit date, contributors, active contributors in the last 90 days, and dependent repositories count.
- **AI-style scoring**: Computes `impact_score`, `maintainer_sustainability_score`, `ecosystem_dependency_score`, `criticality_score`, and a `risk_flag` (`LOW`, `HIGH`, `CRITICAL`).
- **Funding / risk analysis**: When a project is highly depended on but has few/no contributors or no recent commits, Zyntux attaches an `analysis` string highlighting that the project may need funding to continue.
- **Telegram email delivery**: Send the latest top funding candidates to an email address with a PDF report attached.
- **REST API**:
  - `POST /evaluate/topics` – evaluate repositories discovered via topics (with optional `min_stars`).
  - `POST /evaluate/repo` – evaluate a single repository by `repo_url`.
  - `GET /evaluations` – retrieve the most recent evaluation results.

## Project Structure

```text
app/
  config.py
  github_service.py
  crawler.py
  evaluator.py
  main.py
requirements.txt
```

## Configuration

Zyntux uses the GitHub API. For higher rate limits, set a personal access token in the environment:

- **Environment variable**: `GITHUB_TOKEN`
- **Environment variables**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`

You can put this in a `.env` file in the project root:

```env
GITHUB_TOKEN=ghp_your_token_here
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_FROM_EMAIL=bot@example.com
```

## Installation

```bash
cd /home/eversmanxbt/Documents/Programs/hacka
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Usage

### 1. Evaluate by topics

`POST /evaluate/topics`

Request body:

```json
{
  "topics": ["machine-learning", "computer-vision"],
  "min_stars": 100
}
```

Zyntux will:

- Crawl GitHub for each topic with `stars >= min_stars`.
- Collect repository metrics (stars, forks, open issues, creation date, last commit, contributors, active contributors last 90 days, dependents).
- Evaluate up to the top 20 repositories by stars and return scores plus optional `analysis` messages.

### 2. Evaluate a single repository

`POST /evaluate/repo`

Request body:

```json
{
  "repo_url": "https://github.com/owner/repo"
}
```

Zyntux will:

- Fetch metrics for the given repository.
- Compute the same evaluation scores and optional `analysis`.

### 3. Fetch last evaluation results

`GET /evaluations`

Returns the most recent evaluations performed by either `POST /evaluate/topics` or `POST /evaluate/repo`.

