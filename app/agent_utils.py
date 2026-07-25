import json


def process_response(content: str):
    try:
        return json.loads(content)
    except Exception as e:
        print(f"Unable to process JSON content error: {str(e)}")
        return {"conversation": content, "summary": None, "table": "", "graph": ""}
