from __future__ import annotations

from typing import Any, Dict, List


MAX_MESSAGE_LENGTH = 4000
MAX_REPOS_IN_LIST = 20


def _truncate(text: str) -> str:
    if len(text) <= MAX_MESSAGE_LENGTH:
        return text
    return text[: MAX_MESSAGE_LENGTH - 3] + "..."


def format_scan_results(results: Dict[str, Any]) -> str:
    """
    Format the funding candidates from a topic scan into a human-readable
    Telegram message.
    """
    candidates: List[Dict[str, Any]] = results.get("funding_candidates", []) or []
    if not candidates:
        return "No infrastructure funding candidates found for this topic."

    lines: List[str] = []
    lines.append("Infrastructure Funding Candidates")
    lines.append("")

    for candidate in candidates[:MAX_REPOS_IN_LIST]:
        name = candidate.get("full_name", "unknown")
        dependents = candidate.get("dependents_count", 0)
        impact_score = candidate.get("impact_score", 0)
        maintainer_sustainability_score = candidate.get("maintainer_sustainability_score", 0)
        ecosystem_dependency_score = candidate.get("ecosystem_dependency_score", 0)
        criticality_score = candidate.get("criticality_score", 0)
        risk_flag = candidate.get("risk_flag", "UNKNOWN")
        analysis = candidate.get("analysis", "")
        total_contributors = candidate.get("total_contributors", 0)
        open_issues = candidate.get("open_issues", 0)
        active = candidate.get("active_contributors_90d", 0)
        url = candidate.get("html_url", "")

        lines.append(name)
        lines.append(f"Dependents: {dependents:,}")
        lines.append(f"Impact Score: {impact_score}")
        lines.append(f"Maintainer Sustainability Score: {maintainer_sustainability_score}")
        lines.append(f"Ecosystem Dependency Score: {ecosystem_dependency_score}")
        lines.append(f"Criticality Score: {criticality_score}")
        lines.append(f"Open Issues: {open_issues:,}")
        lines.append(f"Total Contributors: {total_contributors:,}")
        lines.append(f"Active Maintainers (90d): {active}")
        lines.append(f"Risk Level: {risk_flag}")
        lines.append(f"Analysis: {analysis}")

        if url:
            lines.append(url)
        lines.append("")  # blank line between entries

    if len(candidates) > MAX_REPOS_IN_LIST:
        remaining = len(candidates) - MAX_REPOS_IN_LIST
        lines.append(f"...and {remaining} more candidates. Use /repo <url> to inspect individually.")

    return _truncate("\n".join(lines).strip())


def format_repo_analysis(results: Dict[str, Any]) -> str:
    """
    Format the result of a single repository analysis.
    """
    candidates: List[Dict[str, Any]] = results.get("funding_candidates", []) or []

    # If the repo is not a funding candidate, still provide a simple message.
    if not candidates:
        return (
            "Repository Analysis\n\n"
            "This repository is not currently flagged as a high-risk funding candidate "
            "based on dependents and maintainer activity."
        )

    c = candidates[0]
    full_name = c.get("full_name", "unknown")
    dependents = c.get("dependents_count", 0)
    impact_score = c.get("impact_score", 0)
    maintainer_sustainability_score = c.get("maintainer_sustainability_score", 0)
    ecosystem_dependency_score = c.get("ecosystem_dependency_score", 0)
    criticality_score = c.get("criticality_score", 0)
    open_issues = c.get("open_issues", 0)
    total_contributors = c.get("total_contributors", 0)
    active = c.get("active_contributors_90d", 0)
    risk = c.get("risk_flag", "UNKNOWN")
    analysis = c.get("analysis", "")

    url = c.get("html_url", "")

    lines: List[str] = []
    lines.append("Repository Analysis")
    lines.append("")
    lines.append(full_name)
    lines.append("")
    lines.append(f"Dependents: {dependents:,}")
    lines.append(f"Impact Score: {impact_score}")
    lines.append(f"Maintainer Sustainability Score: {maintainer_sustainability_score}")
    lines.append(f"Ecosystem Dependency Score: {ecosystem_dependency_score}")
    lines.append(f"Criticality Score: {criticality_score}")
    lines.append(f"Open Issues: {open_issues:,}")
    lines.append(f"Total Contributors: {total_contributors:,}")
    lines.append(f"Active Maintainers (90d): {active}")
    lines.append(f"Risk Level: {risk}")
    lines.append(f"Analysis: {analysis}")

    if url:
        lines.append("")
        lines.append(url)

    return _truncate("\n".join(lines).strip())


def format_funding_targets(results: Dict[str, Any]) -> str:
    candidates = results.get("funding_candidates", []) or []

    if not candidates:
        return "No infrastructure funding targets found."

    lines = []
    lines.append("Top Infrastructure Funding Targets")
    lines.append("")

    for c in candidates[:10]:
        name = c.get("full_name", "unknown")
        dependents = c.get("dependents_count", 0)
        active = c.get("active_contributors_90d", 0)
        impact_score = c.get("impact_score", 0)
        maintainer_sustainability_score = c.get("maintainer_sustainability_score", 0)
        ecosystem_dependency_score = c.get("ecosystem_dependency_score", 0)
        criticality_score = c.get("criticality_score", 0)
        open_issues = c.get("open_issues", 0)
        total_contributors = c.get("total_contributors", 0)
        risk_flag = c.get("risk_flag", "UNKNOWN")
        analysis = c.get("analysis", "")
        url = c.get("html_url", "")

        lines.append(name)
        lines.append(f"Dependents: {dependents:,}")
        lines.append(f"Impact Score: {impact_score}")
        lines.append(f"Maintainer Sustainability Score: {maintainer_sustainability_score}")
        lines.append(f"Ecosystem Dependency Score: {ecosystem_dependency_score}")
        lines.append(f"Criticality Score: {criticality_score}")
        lines.append(f"Open Issues: {open_issues:,}")
        lines.append(f"Total Contributors: {total_contributors:,}")
        lines.append(f"Active Maintainers (90d): {active}")
        lines.append(f"Risk Level: {risk_flag}")
        lines.append(f"Analysis: {analysis}")
        if url:
            lines.append(url)

        lines.append("")

    return _truncate("\n".join(lines).strip())
