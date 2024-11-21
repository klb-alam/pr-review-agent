from github import Github
import os
import asyncio
from dotenv import load_dotenv
from github_retriever import GithubRetriever
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import prompt_templates.grimoire as grimoire

async def analyze_pr(retriever: GithubRetriever) -> None:
    # Create a ChatOpenAI model
    model = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )
    
    # Define prompt template using ChatPromptTemplate

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", grimoire.PR_SUMMARY),
        ("human", "Here are the file changes to analyze: {change_files}")
    ])
    
    chain = prompt_template | model | StrOutputParser()
    
    result = await chain.ainvoke({
        "change_files": retriever.pull_request.change_files
    })
    
    print("\nPull Request Summary:")
    print(result)

async def find_or_create_bot_comment(repo, pr_number, bot_username, comment_body):
    """Finds the bot's previous comment or creates a new one."""
    pr = repo.get_pull(pr_number)
    bot_comment = None

    for comment in pr.get_issue_comments():
        if comment.user.login == bot_username:  # Check if the comment is from the bot
            bot_comment = comment
            break

    if bot_comment:
        bot_comment.edit(body=comment_body)  # Edit the existing comment
    else:
        pr.create_issue_comment(comment_body)  # Create a new comment


async def main():
    load_dotenv(override=False)
    print("Environment variables:", dict(os.environ))
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        raise ValueError("GITHUB_TOKEN not found.")
    

    # dynamic based on pr number input
    pr_number_str = os.getenv("PR_NUMBER") 

    if not pr_number_str:
        raise ValueError("PR_NUMBER environment variable not set.")

    try:
        pr_number = int(pr_number_str)
    except ValueError:
        raise ValueError("Invalid PR_NUMBER format.")

    gh = Github(github_token)
    repo = gh.get_repo("klb-alam/code-challenge") # Replace with your repository name

    retriever = GithubRetriever(gh, repo, pr_number)

    result = await analyze_pr(retriever)

    # Add the review as a comment
    bot_username = os.getenv("GITHUB_ACTOR")  

    # Find or create/update the bot's comment
    await find_or_create_bot_comment(repo, pr_number, bot_username, result)

    gh.close()

if __name__ == "__main__":
    asyncio.run(main())