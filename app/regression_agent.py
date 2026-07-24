from typing import Optional
import nest_asyncio
from app.constants import CAT_MAPS, MODEL_COLUMNS
from app.json_structural_tool import JsonStructuralTool
from app.model_prediction_tool import ModelPredictionTool
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.core.agent import ReActAgent

nest_asyncio.apply()


class RegressionAgent:
    llm: Optional[Anthropic | Ollama | HuggingFaceLLM | BedrockConverse] = None
    json_schema_filepath: str = None
    json_model_filepath: str = None
    model_name: str = None
    system_prompt: str = None
    agent = None

    def __init__(
        self, llm: Optional[Anthropic | Ollama | HuggingFaceLLM | BedrockConverse]
    ):
        json_structural_tool = JsonStructuralTool(
            json_model_filepath=self.json_model_filepath,
            json_schema_filepath=self.json_schema_filepath,
            llm=llm,
        ).tool()

        model_prediction_tool = ModelPredictionTool(
            model_name=self.model_name,
            json_model_filepath=self.json_model_filepath,
            llm=llm,
        ).tool()

        self.agent = ReActAgent(
            tools=[json_structural_tool, model_prediction_tool],
            llm=llm,
            system_prompt=self.system_prompt,
            verbose=True,
        )

    nest_asyncio.apply()

    async def chat(self, prompt: str) -> str:
        response = await self.agent.run(prompt)
        print(response)
        return response
