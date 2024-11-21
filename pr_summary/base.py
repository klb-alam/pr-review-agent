from __future__ import annotations
from typing import Any, Dict, List, Optional
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts import BasePromptTemplate
from pydantic import BaseModel, Field, ConfigDict
from functools import lru_cache
import itertools
from models import PullRequest, PRSummary, ChangeSummary, ChangeFile, ChangeStatus
from pr_summary.prompts import PR_SUMMARY_PROMPT
from processors.pr_processor import PullRequestProcessor

class PRSummaryChain(Chain):


    pr_summary_chain: BaseLanguageModel = Field(..., description="Language model chain for PR summary")
    pr_summary_prompt: BasePromptTemplate = Field(default=PR_SUMMARY_PROMPT)
    output_parser: PydanticOutputParser = Field(
        default_factory=lambda: PydanticOutputParser(pydantic_object=PRSummary)
    )
    
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    
    _input_keys = ["pull_request"]
    _output_keys = ["pr_summary"]

    @property
    def input_keys(self) -> List[str]:
        return self._input_keys

    @property
    def output_keys(self) -> List[str]:
        return self._output_keys

    def _process_pr_summary_input(
        self, 
        pr: PullRequest, 
        code_summaries: List[ChangeSummary]
    ) -> Dict[str, str]:
        """Process PR and code summaries into input format."""
        return {
            "change_files": PullRequestProcessor.gen_material_change_files(pr.change_files),
            "code_summaries": PullRequestProcessor.gen_material_code_summaries(code_summaries),
            "metadata": PullRequestProcessor.gen_material_pr_metadata(pr)
        }

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Async call implementation."""
        _run_manager = run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        await _run_manager.on_text(inputs["pull_request"].json() + "\n")
        
        pr: PullRequest = inputs["pull_request"]
        code_summaries = []  # Initialize empty as we're not processing code summaries
        
        # Generate the input for the prompt
        pr_input = self._process_pr_summary_input(pr, code_summaries)
        
        # Format the prompt
        prompt_value = self.pr_summary_prompt.format_prompt(**pr_input)
        
        # Get response from LLM
        response = await self.pr_summary_chain.agenerate([prompt_value.to_string()])
        
        # Parse the output
        try:
            parsed_output = self.output_parser.parse(response.generations[0][0].text)
            return {"pr_summary": parsed_output.dict()}
        except Exception as e:
            # Fallback to raw text if parsing fails
            return {"pr_summary": response.generations[0][0].text}

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Synchronous call implementation."""
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        _run_manager.on_text(inputs["pull_request"].json() + "\n")
        
        pr: PullRequest = inputs["pull_request"]
        code_summaries = []  # Initialize empty as we're not processing code summaries
        
        # Generate the input for the prompt
        pr_input = self._process_pr_summary_input(pr, code_summaries)
        print("here we fucking go",pr_input)
        
        # Format the prompt
        prompt_value = self.pr_summary_prompt.format_prompt(**pr_input)
        
        
        response = self.pr_summary_chain.generate([prompt_value.to_string()])
        
        # Parse the output
        try:
            parsed_output = self.output_parser.parse(response.generations[0][0].text)
            return {"pr_summary": parsed_output.dict()}
        except Exception as e:
            # Fallback to raw text if parsing fails
            return {"pr_summary": response.generations[0][0].text}

    @classmethod
    def from_llm(
        cls,
        pr_summary_llm: BaseLanguageModel,
        pr_summary_prompt: BasePromptTemplate = PR_SUMMARY_PROMPT,
        **kwargs,
    ) -> PRSummaryChain:
        """Create a PRSummaryChain instance from a language model."""
        output_parser = PydanticOutputParser(pydantic_object=PRSummary)
        return cls(
            pr_summary_chain=pr_summary_llm,
            pr_summary_prompt=pr_summary_prompt,
            output_parser=output_parser,
            **kwargs,
        )