from typing import Optional, List
from pydantic import BaseModel, Field


class Comment(BaseModel):
    """
    Structure to summarize the details of a Pull Request (PR)
    for reviewers to understand it better and faster.
    """

    changes_description: str = Field(
        description="A brief summary of the changes in the PR and its objective."
    )
    pr_category: str = Field(
        description="The category of the PR, e.g., Feature, Fix, Refactor, Perf, Doc, Test, Ci, Style, Housekeeping."
    )
    important_changes: Optional[List[str]] = Field(
        default=None,
        description="A list of important files containing major logical changes, applicable for Feature/Refactor PRs.",
    )
    objective: str = Field(description="The objective of the PR.")
    bugs: Optional[str] = Field(
        default=None,
        description="Potential bugs or issues that the reviewer should pay attention to.",
    )
    errors: Optional[str] = Field(
        default=None,
        description="Discovered errors that will cause code to fail",
    )
