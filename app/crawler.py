from __future__ import annotations

from typing import Any, Dict, List

from .github_service import GitHubService


INFRA_EXCLUDE_KEYWORDS = [
    "course",
    "tutorial",
    "roadmap",
    "awesome",
    "book",
    "learning",
    "bootcamp",
]


class TopicCrawler:
    """
    Crawls GitHub repositories based on provided topics.
    """

    def __init__(self, github_service: GitHubService | None = None) -> None:
        self.github = github_service or GitHubService()

    def _is_infrastructure_repo(self, repo: Dict[str, Any]) -> bool:
        """
        Return False for likely educational / non-infrastructure repos
        based on name or description keywords.
        """
        name = (repo.get("name") or "").lower()
        description = (repo.get("description") or "").lower()
        for kw in INFRA_EXCLUDE_KEYWORDS:
            if kw in name or kw in description:
                return False
        return True

    def crawl_by_topics(self, topics: List[str], min_stars: int) -> List[Dict[str, Any]]:
        """
        Crawl GitHub for each topic with stars >= min_stars, collect
        repository-level metrics, and return a JSON-serializable list
        of repositories limited to the top 20 by stars.

        Metrics collected per repo:
        - full_name (owner/repo)
        - description
        - stars, forks, open_issues
        - creation_date, last_commit
        - total_contributors, active_contributors_90d
        - dependents_count
        """
        if not topics:
            return []

        # Aggregate search results for each topic, handling pagination via GitHubService.
        by_full_name: Dict[str, Dict[str, Any]] = {}
        for topic in topics:
            repos = self.github.search_repositories_by_topic_with_min_stars(
                topic=topic, min_stars=min_stars
            )
            for repo in repos:
                # Skip likely educational / non-infrastructure repositories.
                if not self._is_infrastructure_repo(repo):
                    continue

                full_name = repo.get("full_name")
                if not full_name:
                    continue
                # Prefer the highest-star version if duplicates appear across topics.
                existing = by_full_name.get(full_name)
                if not existing or repo.get("stargazers_count", 0) > existing.get(
                    "stargazers_count", 0
                ):
                    by_full_name[full_name] = repo

        if not by_full_name:
            return []

        # Sort by stars descending and limit to top 20.
        repos_sorted = sorted(
            by_full_name.values(),
            key=lambda r: r.get("stargazers_count", 0),
            reverse=True,
        )[:50]

        # Enrich each repo with the requested metrics using GitHub REST API.
        results: List[Dict[str, Any]] = []
        for repo in repos_sorted:
            full_name = repo["full_name"]
            description = repo.get("description")
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            open_issues = repo.get("open_issues_count", 0)
            created_at = repo.get("created_at")

            last_commit_at = self.github.get_repo_last_commit_date(full_name)
            contributors = self.github.get_repo_contributors(full_name)
            contributors_count = len(contributors)
            active_contributors_90d = self.github.get_active_contributors_last_n_days(
                full_name, days=90
            )
            dependents_count = self.github.get_dependents_count(full_name)

            # Include html_url and GitHub API-style keys so evaluator can consume this.
            results.append(
                {
                    "full_name": full_name,
                    "html_url": f"https://github.com/{full_name}",
                    "description": description,
                    "stargazers_count": stars,
                    "forks_count": forks,
                    "open_issues_count": open_issues,
                    "created_at": created_at,
                    "stars": stars,
                    "forks": forks,
                    "open_issues": open_issues,
                    "creation_date": created_at,
                    "last_commit": last_commit_at.isoformat() if last_commit_at else None,
                    "total_contributors": contributors_count,
                    "active_contributors_90d": active_contributors_90d,
                    "dependents_count": dependents_count,
                }
            )

        return results

