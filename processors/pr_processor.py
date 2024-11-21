from __future__ import annotations

import itertools
from functools import lru_cache
from typing import Callable, Dict, List

from models import ChangeFile, ChangeStatus, ChangeSummary, PullRequest

CONTENT_CHANGE_STATUS = [ChangeStatus.addition, ChangeStatus.modified]

SUPPORT_CODE_FILE_SUFFIX = set(["py", "java", "go", "js", "ts", "php", "c", "cpp", "h", "cs", "rs"])

SUFFIX_LANGUAGE_MAPPING = {
    "py": "python",
    "java": "java",
    "go": "go",
    "js": "javascript",
    "ts": "typescript",
    "php": "php",
    "c": "c",
    "cpp": "cpp",
    "h": "c",
    "cs": "csharp",
    "rs": "rust",
}


class PullRequestProcessor:
    """Process and format pull request information."""
    
    CONTENT_CHANGE_STATUS = [ChangeStatus.addition, ChangeStatus.modified]
    SUPPORT_CODE_FILE_SUFFIX = {
        "py", "java", "go", "js", "ts", "php", 
        "c", "cpp", "h", "cs", "rs"
    }
    
    @staticmethod
    def gen_material_change_files(change_files: List[ChangeFile]) -> str:
        """Generate formatted string of changed files grouped by status."""
        STATUS_HEADER_MAPPING = {
            ChangeStatus.addition: "Added Files:",
            ChangeStatus.modified: "Modified Files:",
            ChangeStatus.deleted: "Deleted Files:",
            ChangeStatus.renaming: "Renamed Files:",
            ChangeStatus.copy: "Copied Files:",
            ChangeStatus.unknown: "Other Changes:"
        }
        
        files_by_status = itertools.groupby(
            sorted(change_files, key=lambda x: x.status), 
            lambda x: x.status
        )
        
        summary_parts = []
        for status, files in files_by_status:
            header = STATUS_HEADER_MAPPING.get(status, STATUS_HEADER_MAPPING[ChangeStatus.unknown])
            file_list = []
            
            for file in files:
                if status == ChangeStatus.copy:
                    file_list.append(f"- {file.full_name} (copied from {file.source_full_name})")
                elif status == ChangeStatus.renaming:
                    file_list.append(f"- {file.full_name} (renamed from {file.source_full_name})")
                else:
                    file_list.append(f"- {file.full_name}")
            
            if file_list:
                summary_parts.append(f"{header}\n" + "\n".join(file_list))
        
        return "\n\n".join(summary_parts)

    @staticmethod
    def gen_material_code_summaries(code_summaries: List[ChangeSummary]) -> str:
        """Generate formatted string of code summaries."""
        return "\n\n".join(
            f"File: {summary.full_name}\n{summary.summary}"
            for summary in code_summaries
        )

    @staticmethod
    def gen_material_pr_metadata(pr: PullRequest) -> str:
        """Generate formatted string of PR metadata."""
        return f"""Pull Request Title: {pr.title}
        Description:
        {pr.body}

        Related Issues:
        {chr(10).join(f'- {issue.title}' for issue in pr.related_issues)}
        """

    @staticmethod
    def build_change_summaries(
        summaries_input: List[Dict[str, str]], 
        summaries_output: List[Dict[str, str]]
    ) -> List[ChangeSummary]:
        """Build list of change summaries from inputs and outputs."""
        return [
            ChangeSummary(full_name=i["name"], summary=o["text"])
            for i, o in zip(summaries_input, summaries_output)
        ]