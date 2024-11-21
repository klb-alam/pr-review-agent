from langchain_core.prompts import PromptTemplate

from prompt_templates import grimoire


PR_SUMMARY_PROMPT = PromptTemplate(
    template=grimoire.PR_SUMMARY,
    input_variables=["change_files"]
)

