from app.agent_utils import process_response
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


# @app.post("/api/v1/chat")
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
    print(json_content)
    table_response = None
    if json_content["table"] is not None or json_content["table"] != "":
        try:
            table_data = json_content["table"]
            if len(table_data) == 0:
                table_response = None
            elif len(table_data) == 1:
                table_response = pd.DataFrame(table_data)
            else:
                table_response = pd.DataFrame(table_data).to_dict(orient="records")
        except Exception as e:
            print(f"Unable to display table with the following error: {str(e)}")
            table_response = None

    # print(json_content["graph"])
    graph_response = None
    if json_content["graph"] is not None or json_content["graph"] != "":
        try:
            # Parse layout configurations out of the dictionary
            chart_dict = json_content["graph"]
            layout_config = chart_dict["layout"]
            x_config = layout_config["xaxis"]

            print("uno")
            print(layout_config)
            print(x_config)
            print(x_config["title"])
            # print(layout_config)

            x_title = (
                x_config["title"]["text"] if x_config["title"] else "Discharge Year"
            )
            print(x_title)

            # Formulate the dynamic wide-format pandas DataFrame
            metrics = [trace["name"] for trace in chart_dict["data"]]
            colors = [trace["marker"]["color"] for trace in chart_dict["data"]]
            print("dos")
            print(colors)

            # Formulate the dynamic wide-format pandas DataFrame
            dataframe_map = {}
            dataframe_map[x_title] = chart_dict["data"][0]["x"]
            # dataframe_map = {'Discharge Year': chart_dict['data'][0]['x']}
            print("tres")
            for trace in chart_dict["data"]:
                dataframe_map[trace["name"]] = trace["y"]
            df = pd.DataFrame(dataframe_map)
            print("quatro")
            print(metrics)
            fig = px.bar(
                df,
                x=x_title,
                y=metrics,
                barmode=layout_config["barmode"],
                color_discrete_sequence=colors,
                title=layout_config["title"]["text"],
                # labels={
                #     'value': layout_config['yaxis']['title'],
                #     'variable': layout_config['legend']['title']['text']
                #     }
            )
            print("cinco")
            # Fine-tune layout properties to match structural configurations
            # fig.update_xaxes(tickmode=x_config['tickmode'], dtick=x_config['dtick'])
            print("seis")
            fig.update_layout(legend_title_text="Prediction Field")
            fig.update_traces(
                textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
            )
            # fig.update_layout(
            #     template=layout_config['template'],
            #     hovermode=layout_config['hovermode']
            #     )
            print("siete")
            graph_response = fig.to_json()
            # x_values = json_content["graph"]["data"][0]["x"]
            # graph_data = json_content["graph"]["data"]
            # y_values = json_content["graph"]["data"][0]["y"]
            # title_value = json_content["graph"]["layout"]["title"]["text"]
            # graph_response = px.bar(x=x_values, y=y_values, title=title_value).to_json()
        except Exception as e:
            print(f"Unable to display graph with the following error: {str(e)}")
            graph_response = None

    final_response = {
        "response": json_content["summary"] or json_content["conversation"],
        "table": table_response,
        "graph": graph_response,
        "status": "success",
    }
    return final_response
