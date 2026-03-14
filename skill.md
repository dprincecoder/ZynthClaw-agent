Zyntux — Open Source Funding Radar

> Automatically identify critical open source infrastructure that powers large ecosystems but has too few maintainers.

## What I do

I crawl GitHub for repositories matching given topics (or a single repo URL),
collect deep maintenance and ecosystem metrics, and surface **funding candidates**:
projects with **high dependents** but **low active contributors**.

For every repository, I:

- Collect metrics: stars, forks, open issues, creation date, last commit date, total contributors, active contributors over the last 90 days, and dependents count.
- Compute scores: `impact_score`, `maintainer_sustainability_score`, `ecosystem_dependency_score`, `criticality_score`, and `risk_flag` (`LOW`, `MEDIUM`, `HIGH`).
- Derive an `analysis` string for fragile backbone projects (for example: “This repository is a critical backbone of the ecosystem with very few active maintainers. High risk of failure if maintainers stop contributing.”).

I then:

- **Prioritize funding candidates**: `dependents_count >= 500` and `active_contributors_90d < 20`.
- **Filter out non-infrastructure repos**: skip obvious educational or “awesome list” style projects.
- Return both the **funding candidates** and **all evaluated repos** for manual review.

## How to use me

Assume the agent is running at:

`BASE_URL=http://127.0.0.1:8000`

### Option A — Evaluate by topics (recommended)

Discover infrastructure projects for one or more GitHub topics.

**Endpoint**

`POST /evaluate/topics`

**Request**

```bash
curl -X POST "$BASE_URL/evaluate/topics" \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["ethereum", "wallet"],
    "min_stars": 500
  }'
```

- **`topics`**: array of GitHub topics to crawl.
- **`min_stars`** (optional, default `0`): minimum stars per repo when searching.

**Response (funding-focused)**

```json
{
  "count": 3,
  "funding_candidates": [
    {
      "full_name": "ethers-io/ethers.js",
      "html_url": "https://github.com/ethers-io/ethers.js",
      "description": "Complete Ethereum wallet implementation and utilities in JavaScript.",
      "total_contributors": 42,
      "open_issues": 128,
      "impact_score": 92.5,
      "dependents_count": 680489,
      "active_contributors_90d": 1,
      "risk_flag": "HIGH",
      "analysis": "This repository is a critical backbone of the ecosystem (680,489 dependents) but has very few active maintainers (1). High risk of failure if maintainers stop contributing."
    }
  ]
}
```

Use this when you want **a ranked list of funding targets** for a topic.

### Option B — Evaluate a single repository

Check whether one specific repo is a funding candidate.

**Endpoint**

`POST /evaluate/repo`

**Request**

```bash
curl -X POST "$BASE_URL/evaluate/repo" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/ethers-io/ethers.js"
  }'
```

**Response (funding-focused)**

```json
{
  "count": 1,
  "funding_candidates": [
    {
      "full_name": "ethers-io/ethers.js",
      "html_url": "https://github.com/ethers-io/ethers.js",
      "description": "...",
      "total_contributors": 42,
      "open_issues": 128,
      "impact_score": 92.5,
      "dependents_count": 680489,
      "active_contributors_90d": 1,
      "risk_flag": "HIGH",
      "analysis": "..."
    }
  ]
}
```

If the repo does **not** meet funding criteria, you’ll get:

```json
{ "count": 0, "funding_candidates": [] }
```

### Option C — Fetch full evaluation context (manual review)

Get **both** the last funding candidates **and** all evaluated projects from the latest request.

**Endpoint**

`GET /evaluations`

**Request**

```bash
curl "$BASE_URL/evaluations"
```

**Response**

```json
{
  "count": 3,
  "funding_candidates": [
    {
      "full_name": "ethers-io/ethers.js",
      "html_url": "https://github.com/ethers-io/ethers.js",
      "description": "...",
      "total_contributors": 42,
      "open_issues": 128,
      "impact_score": 92.5,
      "dependents_count": 680489,
      "active_contributors_90d": 1,
      "risk_flag": "HIGH",
      "analysis": "..."
    }
  ],
  "evaluations_count": 20,
  "evaluations": [
    {
      "full_name": "ethers-io/ethers.js",
      "html_url": "https://github.com/ethers-io/ethers.js",
      "impact_score": 92.5,
      "maintainer_sustainability_score": 34.0,
      "ecosystem_dependency_score": 95.0,
      "criticality_score": 93.75,
      "risk_flag": "HIGH",
      "analysis": "...",
      "metrics": {
        "full_name": "ethers-io/ethers.js",
        "html_url": "https://github.com/ethers-io/ethers.js",
        "description": "...",
        "stars": 65000,
        "forks": 8000,
        "open_issues": 128,
        "created_at": "2016-06-01T00:00:00+00:00",
        "last_commit_at": "2026-03-10T12:34:56+00:00",
        "contributors_count": 42,
        "active_contributors_90d": 1,
        "dependents_count": 680489
      }
    }
  ]
}
```

## Response format (funding candidates)

```json
{
  "count": 3,
  "funding_candidates": [
    {
      "full_name": "owner/repo",
      "html_url": "https://github.com/owner/repo",
      "description": "...",
      "total_contributors": 10,
      "open_issues": 25,
      "impact_score": 78.5,
      "dependents_count": 1200,
      "active_contributors_90d": 3,
      "risk_flag": "HIGH | MEDIUM | LOW",
      "analysis": "Human-readable explanation of risk and funding need."
    }
  ]
}
```

## Rules

- GitHub REST API + HTML scraping only.
- Only public GitHub repositories.
- Filters out likely non-infrastructure repos (names/descriptions containing: `course`, `tutorial`, `roadmap`, `awesome`, `book`, `learning`, `bootcamp`).
- Topic evaluations:
  - Deduplicate repos by `full_name`.
  - Evaluate in parallel for speed.
  - Sort funding candidates by:
    - `dependents_count` descending
    - `active_contributors_90d` ascending
  - Limit to **top 20** funding candidates.

## Endpoints

| Method | Path              | Description                                                       |
|--------|-------------------|-------------------------------------------------------------------|
| POST   | /evaluate/topics  | Crawl topics, evaluate, and return funding candidates             |
| POST   | /evaluate/repo    | Evaluate a single repo as a potential funding candidate           |
| GET    | /evaluations      | Last funding candidates **and** full list of evaluated projects   |

## Goal

Zyntux exists to help funders and ecosystem stewards quickly identify
**open source public goods** that power many other projects but have
too few active maintainers, so those projects can be prioritized for
funding, support, and long-term sustainability.

