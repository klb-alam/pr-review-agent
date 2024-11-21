from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
# from unidiff import PatchedFile


class DiffSegment(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """Added lines count of this segment."""
    add_count: int = Field()
    """Removed lines count of this segment."""
    remove_count: int = Field()
    """Diff content of this segment."""
    content: str = Field()
    """Start line number of this segment in source file."""
    source_start_line_number: int = Field()
    """Length of this segment in source file."""
    source_length: int = Field()
    """Start line number of this segment in target file."""
    target_start_line_number: int = Field()
    """Length of this segment in target file."""
    target_length: int = Field()
   


class DiffContent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    add_count: int = Field()
    """Added lines count."""
    remove_count: int = Field()
    """Removed lines count."""
    content: str = Field()
    """Diff content."""
    diff_segments: list[DiffSegment] = Field(default_factory=list, exclude=True)
    """Diff segments."""
    """Unidiff patched file object."""
