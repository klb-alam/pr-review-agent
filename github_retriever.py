from __future__ import annotations
from github import Github
from github.PullRequest import PullRequest as GHPullRequest
from github.Repository import Repository as GHRepo
from github.File import File as GithubFile
from utils.diff_utils import parse_patch_file
from models import Repository,PullRequest,ChangeFile,DiffContent,DiffSegment,ChangeStatus



class GithubRetriever():
    """Github retriever."""

    GITHUB_STATUS_MAPPING = {
        "added": "A",
        "copied": "C",
        "removed": "D",
        "modified": "M",
        "renamed": "R",
        "type_change": "T",
    }

    ISSUE_PATTERN = r"#\d+"

    def __init__(
        self,
        client: Github,
        repository_name_or_id: str | int,
        pull_request_number: int,
    ):
        if isinstance(repository_name_or_id, Repository):
            repository_name_or_id = repository_name_or_id.full_name  

        self._git_repository: GHRepo = client.get_repo(repository_name_or_id)
        self._git_pull_request: GHPullRequest = self._git_repository.get_pull(
            pull_request_number
        )

        self._repository = self._build_repository(self._git_repository)
        self._pull_request = self._build_pull_request(self._git_pull_request)


    @property
    def repository(self) -> Repository:
        return self._repository

    @property
    def pull_request(self) -> PullRequest:
        return self._pull_request
    
    @property
    def source_repository(self) -> Repository:
        """Get the source repository (fork) if different from base repository."""
        if self._git_pull_request.head.repo.id != self._git_repository.id:
            return self._build_repository(self._git_pull_request.head.repo)
        return self.repository

    def _build_repository(self, git_repo: GHRepo) -> Repository:
        """Build a Repository object from a GHRepo instance."""
        return Repository(
            repository_id=git_repo.id,
            repository_name=git_repo.name,
            repository_full_name=git_repo.full_name,
            repository_url=git_repo.html_url,
            raw=git_repo,
        )

    def _build_pull_request(self, git_pr: GHPullRequest) -> PullRequest:
        change_files = self._build_change_file_list(git_pr)

        return PullRequest(
            pull_request_id=git_pr.id,
            repository_id=git_pr.head.repo.id,
            pull_request_number=git_pr.number,
            title=git_pr.title,
            body=git_pr.body if git_pr.body is not None else "",
            url=git_pr.html_url,
            repository_name=git_pr.head.repo.full_name,
            change_files=change_files,
            repository=self.repository,
            source_repository=self.source_repository,
            raw=git_pr,
        )
    
    def _build_change_file_list(self, git_pr: GHPullRequest) -> list[ChangeFile]:
        change_files = []
        for file in git_pr.get_files():
            change_file = self._build_change_file(file, git_pr)
            change_files.append(change_file)
        return change_files
    
    def _build_change_file(
        self, git_file: GithubFile, git_pr: GHPullRequest
    ) -> ChangeFile:
        full_name = git_file.filename
        name = full_name.split("/")[-1]
        suffix = name.split(".")[-1]
        source_full_name = (
            git_file.previous_filename if git_file.previous_filename else full_name
        )

        return ChangeFile(
            blob_id=int(git_file.sha, 16),
            sha=git_file.sha,
            full_name=full_name,
            source_full_name=source_full_name,
            name=name,
            suffix=suffix,
            status=self._convert_status(git_file.status),
            pull_request_id=git_pr.id,
            start_commit_id=int(git_pr.base.sha, 16),
            end_commit_id=int(git_pr.head.sha, 16),
            diff_url=self._build_change_file_diff_url(git_file, git_pr),
            blob_url=git_file.blob_url,
            diff_content=self._parse_and_build_diff_content(git_file),
            raw=git_file,
        )
    
    def _convert_status(self, git_status: str) -> ChangeStatus:
        return ChangeStatus(GithubRetriever.GITHUB_STATUS_MAPPING.get(git_status, "X"))

    def _build_change_file_diff_url(
        self, git_file: GithubFile, git_pr: GHPullRequest
    ) -> str:
        return f"{git_pr.html_url}/files#diff-{git_file.sha}"
    

    def _parse_and_build_diff_content(self, git_file: GithubFile) -> DiffContent:
        patched_file = self._build_patched_file(git_file)
        patched_segs: list[DiffSegment] = self._build_patched_file_segs(patched_file)

        # TODO: retrive long content from blob.
        return DiffContent(
            add_count=patched_file.added,
            remove_count=patched_file.removed,
            content=git_file.patch if git_file.patch else "",
            diff_segments=patched_segs,
        )
    
    def _build_patched_file(self, git_file: GithubFile):
        prev_name = (
            git_file.previous_filename
            if git_file.previous_filename
            else git_file.filename
        )
        return parse_patch_file(git_file.patch, prev_name, git_file.filename)
    
    def _build_patched_file_segs(self, patched_file) -> list[DiffSegment]:
        patched_segs = []
        for patched_hunk in patched_file:
            patched_segs.append(self._build_patch_segment(patched_hunk))
        return patched_segs
    
    def _build_patch_segment(self, patched_hunk) -> DiffSegment:
        return DiffSegment(
            add_count=patched_hunk.added or 0,
            remove_count=patched_hunk.removed or 0,
            content=str(patched_hunk),
            source_start_line_number=patched_hunk.source_start,
            source_length=patched_hunk.source_length,
            target_start_line_number=patched_hunk.target_start,
            target_length=patched_hunk.target_length,
        )
    

    def get_repository(self) -> Repository:
        """Get the repository details."""
        return self._build_repository(self._git_repository)

    





# def get_pull_request_files(self) -> list[dict]:
#         """Get the list of files changed in the pull request with their statuses and contents."""
#         files = self._git_pull_request.get_files()
#         pull_request_head_sha = self._git_pull_request.head.sha

#         file_details = []
#         for file in files:
#             file_info = {
#                 "filename": file.filename,
#                 "status": self.GITHUB_STATUS_MAPPING.get(file.status, file.status),
#                 "additions": file.additions,
#                 "deletions": file.deletions,
#                 "changes": file.changes,
#                 "patch": file.patch,  # Diff of the changes
#             }

#             # Fetch the file content if the file is not deleted
#             if file.status != "removed":
#                 try:
#                     contents = self._git_repository.get_contents(file.filename, ref=pull_request_head_sha)
#                     file_info["content"] = base64.b64decode(contents.content).decode('utf-8')
#                 except Exception as e:
#                     file_info["content"] = f"Error fetching content: {str(e)}"
#             else:
#                 file_info["content"] = None  # No content for removed files

#             file_details.append(file_info)

#         return file_details
