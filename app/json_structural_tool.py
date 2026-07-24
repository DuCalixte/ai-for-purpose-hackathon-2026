import json
from typing import Optional
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.core.indices.struct_store import JSONQueryEngine

from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool

from dotenv import load_dotenv

# Load the .env file
load_dotenv()


class JsonStructuralTool:
    llm: Optional[Anthropic | Ollama | HuggingFaceLLM | BedrockConverse] = None
    json_schema = None
    json_model = None

    def __init__(
        self,
        json_model_filepath: str,
        json_schema_filepath: str,
        llm: Optional[Anthropic | Ollama | HuggingFaceLLM | BedrockConverse],
    ):
        self.llm = llm

        # Loading the model to use
        with open(json_model_filepath, "r") as file:
            self.json_model = json.load(file)

        # Loading the model to use
        with open(json_schema_filepath, "r") as file:
            self.json_schema = json.load(file)

    def tool(self):
        query_engine = JSONQueryEngine(
            json_value=self.json_model, json_schema=self.json_schema, llm=self.llm
        )

        return QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name="xgboost_structure_tool",
                description="Queries the JSON architecture. Use it to check metadata, tree depths, configurations, or split thresholds.",
            ),
        )
