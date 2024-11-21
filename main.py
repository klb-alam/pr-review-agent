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

async def main():
    """Main entry point for the PR analysis tool."""
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        raise ValueError("Please set the GITHUB_TOKEN environment variable.")

    gh = Github(github_token)
    retriever = GithubRetriever(gh, "klb-alam/code-challenge", 1)
    
    try:
        await analyze_pr(retriever)
    except Exception as e:
        print(f"Error analyzing pull request: {e}")
    finally:
        gh.close()

if __name__ == "__main__":
    asyncio.run(main())