"""DataverseNO adapter for repository #6."""
from __future__ import annotations

from dataverse_adapter import discover_dataverse
from common import Candidate


def discover(repo: dict, queries: list[str]) -> list[Candidate]:
    return discover_dataverse(repo, queries)
