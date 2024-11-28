from github import Github
import os
import asyncio
from dotenv import load_dotenv
from github_retriever import GithubRetriever, ChangeFile
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import prompt_templates.grimoire as grimoire
from utils.output_struc import Comment


async def analyze_pr(retriever: GithubRetriever):
    llm = ChatOpenAI(
        api_key=os.getenv("INPUT_OPENAI_API_KEY"), model="gpt-4o-mini", max_retries=2
    )
    structured_llm = llm.with_structured_output(Comment)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", grimoire.PR_SUMMARY),
            ("human", "Here are the file changes to analyze: {change_files}"),
        ]
    )

    chain = prompt_template | structured_llm

    result = await chain.ainvoke({"change_files": retriever.pull_request.change_files})

    return result


def find_or_create_bot_comment(
    repo, pr_number, bot_username, comment_body, retriever: GithubRetriever
):
    changes_description = comment_body.changes_description
    pr_category = comment_body.pr_category
    important_changes = comment_body.important_changes
    objective = comment_body.objective
    pr = repo.get_pull(pr_number)

    # Construct the "Important Changes" section with URLs
    important_changes_with_urls = []
    for change in important_changes:
        # Find the corresponding diff URL
        diff_url = next(
            (
                change_file.diff_url
                for change_file in retriever.pull_request.change_files
                if change in change_file.full_name
            ),
            None,
        )
        if diff_url:
            important_changes_with_urls.append(f"[{change}]({diff_url})")
        else:
            important_changes_with_urls.append(change)

    comment_body = (
        f"### Changes Description\n{changes_description}\n\n"
        f"### PR Category\n{pr_category}\n\n"
        f"### Important Changes\n{', '.join(important_changes_with_urls)}\n\n"
        f"### Objective\n{objective}"
    )

    bot_comment = None
    for comment in pr.get_issue_comments():
        if comment.user.login == bot_username:
            bot_comment = comment
            break

    if bot_comment:
        bot_comment.edit(body=comment_body)
    else:
        pr.create_issue_comment(body=comment_body)


async def main():
    load_dotenv(override=False)
    github_token = os.getenv("INPUT_GITHUB_TOKEN")

    if not github_token:
        raise ValueError("GITHUB_TOKEN not found.")

    pr_number_str = os.getenv("INPUT_PR_NUMBER")

    if not pr_number_str:
        raise ValueError("PR_NUMBER environment variable not set.")

    try:
        pr_number = int(pr_number_str)
    except ValueError:
        raise ValueError("Invalid PR_NUMBER format.")

    gh = Github(github_token)
    repo = gh.get_repo("klb-alam/code-challenge")

    retriever = GithubRetriever(gh, repo.full_name, pr_number)

    result = await analyze_pr(retriever)

    bot_username = os.getenv("GITHUB_ACTOR")

    find_or_create_bot_comment(repo, pr_number, bot_username, result, retriever)

    gh.close()


if __name__ == "__main__":
    asyncio.run(main())
