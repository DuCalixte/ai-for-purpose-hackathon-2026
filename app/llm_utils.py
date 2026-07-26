import os
import json
from typing import Optional
import torch

from dotenv import load_dotenv
from app.constants import (
    ANTHROPIC_LLM_MODEL,
    ANTHROPIC_MAX_TOKENS,
    AWS_REGION,
    BEDROCK_LLM_MODEL,
    BEDROCK_MAX_TOKENS,
    DEFAULT_NUM_GPU,
    HUGGING_FACE_CONTEXT_WINDOW,
    HUGGING_FACE_LLM_MODEL,
    HUGGING_FACE_MAX_NEW_TOKENS,
    HUGGING_FACE_TEMPERATURE,
    HUGGING_FACE_TOKENIZER_MODEL,
    LLM_TO_USE,
    OLLAMA_DEFAULT_TIMEOUT,
    OLLAMA_LLM_MODEL,
    OLLAMA_MAX_MEMORY,
    OLLAMA_MAX_TOKENS,
)

# Load the .env file
load_dotenv()

from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.bedrock_converse import BedrockConverse


def acquire_model() -> Optional[Anthropic | Ollama | HuggingFaceLLM | BedrockConverse]:
    match LLM_TO_USE:
        case "Anthropic":
            return Anthropic(model=ANTHROPIC_LLM_MODEL, max_tokens=8192)
        case "Ollama":
            return Ollama(
                model=OLLAMA_LLM_MODEL,
                request_timeout=OLLAMA_DEFAULT_TIMEOUT,
                additional_kwargs={
                    "num_predict": OLLAMA_MAX_TOKENS,  # Generates up to 4096 tokens
                    "num_ctx": OLLAMA_MAX_MEMORY,  # Large 16K memory pool for prompt + response
                    "num_gpu": DEFAULT_NUM_GPU,  # Tells Ollama to use your 8 GPU cores automatically
                },
            )
        case "HuggingFace":
            return HuggingFaceLLM(
                model_name=HUGGING_FACE_LLM_MODEL,
                tokenizer_name=HUGGING_FACE_TOKENIZER_MODEL,
                context_window=HUGGING_FACE_CONTEXT_WINDOW,  # Replaces num_ctx
                max_new_tokens=HUGGING_FACE_MAX_NEW_TOKENS,  # Replaces num_predict / max_tokens
                device_map="auto",  # Automatically chooses MPS (Mac) or CUDA (Nvidia)
                model_kwargs={
                    "torch_dtype": torch.float16  # Runs in FP16 precision
                },
                generate_kwargs={
                    "temperature": HUGGING_FACE_TEMPERATURE,
                    "do_sample": True,
                },
            )
        case "AmazonBedrock":
            return BedrockConverse(
                model=BEDROCK_LLM_MODEL,
                max_tokens=BEDROCK_MAX_TOKENS,
                region_name=AWS_REGION,
            )
        case _:
            return None


llm_to_use = acquire_model()
