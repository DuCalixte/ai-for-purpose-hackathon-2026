import json
import xgboost as xgb
import numpy as np
import pandas as pd
from typing import Optional
from app.constants import CAT_MAPS, MODEL_COLUMNS
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent


class ModelPredictionTool:
    llm: Optional[Anthropic | Ollama | HuggingFaceLLM | BedrockConverse] = None
    model_name: str = ""
    json_model_filepath: str = ""
    model_columns: dict = MODEL_COLUMNS
    categories: dict = CAT_MAPS

    def __init__(
        self,
        json_model_filepath: str,
        llm: Optional[Anthropic | Ollama | HuggingFaceLLM | BedrockConverse],
        model_name: str,
        model_columns: Optional[dict] = None,
        categories: Optional[dict] = None,
    ):
        self.llm = llm
        self.json_model_filepath = json_model_filepath
        if categories is not None:
            self.categories = categories

        if model_columns is not None:
            self.model_columns = model_columns
        self.model_name = model_name

    def predict_from_model(self, input_dict: dict) -> Optional[float]:
        """Accepts grouped parameters, maps to integer array, and executes named DMatrix."""
        try:
            print(input_dict)
            encoded_features = {col: 0 for col in self.model_columns}

            for item in self.model_columns:
                if item in input_dict:
                    if item in ["discharge_year", "length_of_stay"]:
                        encoded_features[item] = int(input_dict[item])
                    else:
                        encoded_features[item] = input_dict[item]

            integer_row = [int(encoded_features[col]) for col in self.model_columns]
            print(integer_row)

            bst = xgb.Booster()
            bst.load_model(self.json_model_filepath)

            data_matrix = xgb.DMatrix(
                np.array([integer_row], dtype=int), feature_names=self.model_columns
            )
            # return float(bst.predict(data_matrix)[0])
            prediction = float(bst.predict(data_matrix)[0])
            print(f"prediction is {prediction}")
            return prediction
        except Exception as e:
            print(f"Prediction failed: {str(e)}")
            return None

    def tool(self):
        return FunctionTool.from_defaults(
            fn=self.predict_from_model,
            name="xgboost_prediction_tool",
            description=f"Calculates healthcare data predictions with {self.model_name}. Accepts a dictionary of readable active metrics.",
        )
