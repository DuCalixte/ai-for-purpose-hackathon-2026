from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import HTMLResponse
# from app.agent import agent
from app.auth import validate_key
from app.config import Settings
import pandas as pd
import plotly.express as px
from pydantic import BaseModel

settings = Settings()

app = FastAPI(
    title=settings.APP_NAME,
    open_api_url=f"{settings.API_V1_STR}/openapi.json"
)

# async def verify_key(x_api_key: str = Header(...)):
#     print("...............................................")
#     print(x_api_key)
#     print("...............................................")
#     # if not validate_key(x_api_key): raise HTTPException(403)
#     return True

async def verify_key(x_api_key: str = Header(...)):
    if not validate_key(x_api_key): raise HTTPException(403)

@app.get("/")
def read_root():
    return { "message": "NYC Reimbursement API is running. Go to /ui for Chatbot." }

@app.get(settings.APP_STATUS)
def app_status():
    return { "status": "OK" }

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

# @app.post("/api/v1/chat", dependencies=[Depends(verify_key)])
# @app.post("/api/v1/chat")
# async def chat(query: str):
#     print(query)
    
#     print("...............................................")
#     body = {
#             "response": "hellow world, it is I",
#             "table": pd.DataFrame({'Data': [1, 2, 3]}), 
#             "graph": px.bar(x=[1, 2, 3], y=[10, 20, 30])
#         }
#     return body
#     # return {"response": str("agent.chat(query)")}
class ChatRequest(BaseModel):
    query: str

# @app.post("/api/v1/chat")
@app.post("/api/v1/chat", dependencies=[Depends(verify_key)])
async def chat(request: ChatRequest):
    print(request.query)
    
    # Convert complex objects to JSON-compatible structures
    body = {
        "response": "hellow world, it is I",
        "table": pd.DataFrame({"Data": [1, 2, 3]}).to_dict(orient="records"),
        "graph": px.bar(x=[1, 2, 3], y=[10, 20, 30]).to_json(),
        "status": "success"
    }
    return body