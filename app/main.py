from app.agent_utils import draw_graph, process_response
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import HTMLResponse
from app.agent import Agent
from app.auth import validate_key
from app.config import Settings
import pandas as pd
import plotly.express as px
from pydantic import BaseModel
import json
import re
import traceback
import numpy as np


class ChatRequest(BaseModel):
    query: str
    session_id: str


class ChatResponse(BaseModel):
    query: str


settings = Settings()

app = FastAPI(
    title=settings.APP_NAME, open_api_url=f"{settings.API_V1_STR}/openapi.json"
)


async def verify_key(x_api_key: str = Header(...)):
    if not validate_key(x_api_key):
        raise HTTPException(403)


@app.get("/")
def read_root():
    return {"message": "NYC Reimbursement API is running. Go to /ui for Chatbot."}


@app.get(settings.APP_STATUS)
def app_status():
    return {"status": "OK"}


@app.get("/dashboard", response_class=HTMLResponse)
def display_streamlit_app():
    # Replace the src URL with your live or local Streamlit instance port
    html_content = """
    <html>
        <head>
            <title>FastAPI Dashboard Portal</title>
        </head>
        <body style="margin:0; padding:0; overflow:hidden;">
            <iframe src="http://localhost:8501/?embed=true" 
                    style="width:100%; height:100vh; border:none;">
            </iframe>
        </body>
    </html>
    """
    return html_content


@app.post("/api/v1/chat", dependencies=[Depends(verify_key)])
async def chat(request: ChatRequest):
    print(request.query)
    session_id = request.session_id
    query = request.query
    agent = Agent(session_id=session_id)
    body = await agent.chat(query)
    print(body)
    content = re.sub(
        r"^```json\s*|```$", "", body.response.content.strip(), flags=re.IGNORECASE
    )
    print(content)
    json_content = process_response(content)  # json.loads(content)

    table_response = None
    if json_content.get("table"):
        try:
            table_data = json_content["table"]
            if len(table_data) == 0:
                table_response = None
            elif len(table_data) == 1:
                table_response = pd.DataFrame(table_data).to_dict(orient="records")
            else:
                table_response = pd.DataFrame(table_data).to_dict(orient="records")
        except Exception as e:
            print(f"Unable to display table with the following error: {str(e)}")
            table_response = None

    # print(json_content["graph"])
    graph_response = None
    if json_content.get("graph"):
        graph_response = draw_graph(json_content.get("graph", {}))

    final_response = {
        "response": json_content["summary"] or json_content["conversation"],
        "table": table_response,
        "graph": graph_response,
        "status": "success",
    }
    return final_response
