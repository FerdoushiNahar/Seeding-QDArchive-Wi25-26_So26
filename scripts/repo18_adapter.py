"""Murray Research Archive adapter for repository #18.

The Murray site points to its Dataverse collection at Harvard Dataverse.
This adapter therefore queries the Dataverse API with subtree='mra'.
"""
from __future__ import annotations

from dataverse_adapter import discover_dataverse
from common import Candidate


def discover(repo: dict, queries: list[str]) -> list[Candidate]:
    return discover_dataverse(repo, queries)
