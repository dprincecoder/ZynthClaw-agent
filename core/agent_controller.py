from __future__ import annotations

from typing import Any, Dict

from app.crawler import TopicCrawler
from app.evaluator import Evaluator
from app.github_service import GitHubService
from app.main import (
    TopicsEvaluateRequest,
    RepoEvaluateRequest,
    evaluate_topics,
    evaluate_repo,
    FundingCandidatesEnvelope,
    get_last_funding_targets,
)


def _build_services() -> tuple[Evaluator, TopicCrawler]:
    """
    Construct evaluator and crawler services sharing a single GitHubService
    instance so that the controller can reuse the same logic as the FastAPI
    endpoints without going through HTTP.
    """
    github_service = GitHubService()
    evaluator = Evaluator(github_service=github_service)
    crawler = TopicCrawler(github_service=github_service)
    return evaluator, crawler


def scan_topic(topic: str, min_stars: int = 0) -> Dict[str, Any]:
    """
    Evaluate repositories for a single topic using the existing
    /evaluate/topics logic and return the FundingCandidatesEnvelope
    as a plain dict.
    """
    evaluator, crawler = _build_services()
    request = TopicsEvaluateRequest(topics=[topic], min_stars=min_stars)
    envelope = evaluate_topics(request, evaluator=evaluator, crawler=crawler)
    return envelope.model_dump()


def scan_repo(repo_url: str) -> Dict[str, Any]:
    """
    Evaluate a single repository using the existing /evaluate/repo logic
    and return the FundingCandidatesEnvelope as a plain dict.
    """
    evaluator, _ = _build_services()
    request = RepoEvaluateRequest(repo_url=repo_url)
    envelope = evaluate_repo(request, evaluator=evaluator)
    return envelope.model_dump()


def get_funding_targets() -> Dict[str, Any]:
    """
    Return the last funding targets as a plain dict.
    """
    envelope = get_last_funding_targets()
    return envelope.model_dump()
    