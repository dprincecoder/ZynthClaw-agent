from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from concurrent.futures import ThreadPoolExecutor

from .github_service import GitHubService


@dataclass
class RepositoryMetrics:
    full_name: str
    html_url: str
    description: Optional[str]
    stars: int
    forks: int
    open_issues: int
    created_at: datetime
    last_commit_at: Optional[datetime]
    contributors_count: int
    active_contributors_90d: int
    dependents_count: Optional[int]


@dataclass
class RepositoryEvaluation:
    full_name: str
    html_url: str
    metrics: RepositoryMetrics
    impact_score: float
    maintainer_sustainability_score: float
    ecosystem_dependency_score: float
    criticality_score: float
    risk_flag: str
    analysis: Optional[str] = None


class Evaluator:
    """
    Computes evaluation scores for repositories based on collected metrics.
    Scoring is heuristic and can be refined over time.
    """

    def __init__(self, github_service: GitHubService | None = None) -> None:
        self.github = github_service or GitHubService()

    def collect_metrics_from_repo_obj(self, repo: Dict[str, Any]) -> RepositoryMetrics:
        full_name = repo["full_name"]
        html_url = repo["html_url"]
        description = repo.get("description")
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        open_issues = repo.get("open_issues_count", 0)
        created_at_str = repo.get("created_at")
        created_at = (
            datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            if created_at_str
            else datetime.now(timezone.utc)
        )

        last_commit_at = self.github.get_repo_last_commit_date(full_name)
        contributors = self.github.get_repo_contributors(full_name)
        contributors_count = len(contributors)
        active_contributors_90d = self.github.get_active_contributors_last_n_days(
            full_name, days=90
        )
        dependents_count = self.github.get_dependents_count(full_name)

        return RepositoryMetrics(
            full_name=full_name,
            html_url=html_url,
            description=description,
            stars=stars,
            forks=forks,
            open_issues=open_issues,
            created_at=created_at,
            last_commit_at=last_commit_at,
            contributors_count=contributors_count,
            active_contributors_90d=active_contributors_90d,
            dependents_count=dependents_count,
        )

    def evaluate_repository(self, metrics: RepositoryMetrics) -> RepositoryEvaluation:
        """
        Derive multiple scores from raw metrics.
        All scores are normalized to 0–100.
        """
        now = datetime.now(timezone.utc)

        # Impact: mostly stars and forks, with light weight to dependents
        star_score = min(metrics.stars / 1000.0 * 100, 100)  # 0–100 for up to 1000 stars
        fork_score = min(metrics.forks / 200.0 * 100, 100)  # 0–100 for up to 200 forks
        dep_raw = metrics.dependents_count or 0
        dep_score = min(dep_raw / 1000.0 * 100, 100)
        impact_score = 0.6 * star_score + 0.3 * fork_score + 0.1 * dep_score

        # Maintainer sustainability: contributors and active contributors ratio
        contrib_score = min(metrics.contributors_count / 20.0 * 100, 100)
        active_score = min(metrics.active_contributors_90d / 10.0 * 100, 100)
        maintainer_sustainability_score = 0.5 * contrib_score + 0.5 * active_score

        # Ecosystem dependency: dependents and forks
        ecosystem_dependency_score = 0.7 * dep_score + 0.3 * fork_score

        # Criticality: combination of impact and ecosystem dependency
        criticality_score = 0.5 * impact_score + 0.5 * ecosystem_dependency_score

        # Fragility-based risk evaluation using dependents_count and active_contributors_90d
        dep_count = metrics.dependents_count if metrics.dependents_count is not None else 0
        active = metrics.active_contributors_90d

        if metrics.dependents_count is not None:
            if dep_count > 1000 and active <= 10:
                risk_flag = "HIGH"
                analysis = (
                    f"This repository is a critical backbone of the ecosystem "
                    f"({dep_count:,} dependents) but has very few active maintainers ({active}). "
                    "High risk of failure if maintainers stop contributing."
                )
            elif dep_count > 500 and active <= 5:
                risk_flag = "MEDIUM"
                analysis = (
                    f"This repository is widely depended on ({dep_count:,} dependents). "
                    "Consider funding or increasing maintainer support."
                )
            else:
                risk_flag = "LOW"
                analysis = "No immediate risk detected."
        else:
            risk_flag = "LOW"
            analysis = "Insufficient data to determine risk."

        print(
            f"[Risk Evaluation] {metrics.full_name}: risk={risk_flag}, "
            f"dependents={dep_count}, active_contributors={active}"
        )

        return RepositoryEvaluation(
            full_name=metrics.full_name,
            html_url=metrics.html_url,
            metrics=metrics,
            impact_score=round(impact_score, 2),
            maintainer_sustainability_score=round(maintainer_sustainability_score, 2),
            ecosystem_dependency_score=round(ecosystem_dependency_score, 2),
            criticality_score=round(criticality_score, 2),
            risk_flag=risk_flag,
            analysis=analysis,
        )

    def _evaluate_from_repo(self, repo: Dict[str, Any]) -> RepositoryEvaluation:
        metrics = self.collect_metrics_from_repo_obj(repo)
        return self.evaluate_repository(metrics)

    def evaluate_repositories(self, repos: List[Dict[str, Any]]) -> List[RepositoryEvaluation]:
        """
        Evaluate repositories in parallel to improve throughput.
        """
        if not repos:
            return []

        with ThreadPoolExecutor(max_workers=8) as executor:
            evaluations = list(executor.map(self._evaluate_from_repo, repos))

        return evaluations

