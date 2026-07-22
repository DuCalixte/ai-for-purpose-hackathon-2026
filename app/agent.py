import os
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.core.tools import FunctionTool
from app.mcp_server import mcp
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from dotenv import load_dotenv

load_dotenv() 

llm = HuggingFaceInferenceAPI(
    model_name="meta-llama/Meta-Llama-3-8B-Instruct",
    token=os.environ.get("HF_TOKEN")
)

# 1. Define a tool
def multiply(a: int, b: int) -> int:
    """Useful for multiplying two numbers together."""
    return a * b

multiply_tool = FunctionTool.from_defaults(fn=multiply)

transport = StdioTransport(
    command="python",
    args=["mcp_server.py", "--verbose"],
    env={"LOG_LEVEL": "DEBUG"},
    cwd="app"
)
# client = Client("./mcp_server")

# Export MCP tools to LlamaIndex
# tools = mcp.list_tools()
# async with client:
#     tools = await client.list_tools()

# agent = ReActAgent.from_tools(
#     tools=tools,
#     llm=llm,
#     system_prompt="You are an NYC healthcare reimbursement assistant. Provide estimates based on the model. Never process PII.",
#     verbose=True
# )

async def main():
    # Connect to your FastMCP server script
    # client = Client("./mcp_server")
    client = Client(transport)

    
    async with client:
        # Retrieve all available operations and tools on the server
        tools = await client.list_tools()
        
        print("Available Tools:")
        for tool in tools:
            print(f"- Name: {tool.name}")
            print(f"  Description: {tool.description}")
            print(f"  Parameters: {tool.inputSchema}\n")
        
        agent = None
        # agent = ReActAgent.create_from_tools(
        #     tools=tools,
        #     llm=llm,
        #     system_prompt="You are an NYC healthcare reimbursement assistant. Provide estimates based on the model. Never process PII.",
        #     verbose=True)
        # agent = await ReActAgent.from_tools(llm=llm, verbose=True)


# Run the async client
asyncio.run(main())
