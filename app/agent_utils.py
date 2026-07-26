import json
from typing import Dict, Any, Optional
import pandas as pd
import plotly.express as px
import traceback


def process_response(content: str):
    try:
        return json.loads(content)
    except Exception as e:
        print(f"Unable to process JSON content error: {str(e)}")
        return {"conversation": content, "summary": None, "table": "", "graph": ""}


def draw_graph(chart_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Get layout
    try:
        x_title = "Discharge Year"
        barmode = "group"
        graph_title = "Discharge by year"
        layout_config = chart_dict.get("layout", None)
        if layout_config:
            barmode = layout_config.get("barmode", "group")
            x_config = layout_config.get("xaxis", None)
            graph_title = __get_value(layout_config, "title", "text", "Discharge Year")
            if x_config:
                x_title = __get_value(x_config, "title", "text", "Discharge Year")

        data_graph = chart_dict.get("data", None)
        metrics = ["Discharge"]
        colors = ["#1f77b4"]
        if data_graph:
            metrics = [trace.get("name", "Discharge") for trace in data_graph]
            colors = [
                trace.get("marker", {}).get("color", "#1f77b4") for trace in data_graph
            ]

            dataframe_map = {}
            dataframe_map[x_title] = data_graph[0]["x"]
            for trace in data_graph:
                dataframe_map[trace["name"]] = trace["y"]
            df = pd.DataFrame(dataframe_map)

        fig = px.bar(
            df,
            x=x_title,
            y=metrics,
            barmode=barmode,
            color_discrete_sequence=colors,
            title=graph_title,
        )
        fig.update_layout(legend_title_text="Prediction Field")
        fig.update_traces(
            textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
        )

        return fig.to_json()
    except Exception as e:
        traceback.print_exc()
        print(f"Unable to display graph with the following error: {str(e)}")
        return None


def __get_value(data: Dict[str, Any], first: str, second: str, default: str) -> str:
    first_result = title_data = data.get(first)
    if first_result and isinstance(first_result, dict):
        result = title_data.get(second, default)
    else:
        result = first_result if first_result else default
    return result
