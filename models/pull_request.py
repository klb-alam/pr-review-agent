from typing import Any

from pydantic import BaseModel, Field
from models.change_file import ChangeFile

class PullRequest(BaseModel):
    """Pull Request id (Global id. Not number/iid)"""
    pull_request_id: int = Field()  
    """Repository id this pull request belongs to."""
    repository_id: int = Field()
    pull_request_number: int = Field(default=0)
    """Pull Request title."""
    title: str = Field(default="")
    """Pull Request description."""
    body: str = Field(default="")
    """Pull Request url."""
    url: str = Field(default="")
    change_files: list[ChangeFile] = Field(default_factory=list, exclude=True)
    """Repository name this pull request belongs to."""
    repository_name: str = Field(default="")
    """git PR raw object"""
    raw: object = Field(default=None, exclude=True)
   
