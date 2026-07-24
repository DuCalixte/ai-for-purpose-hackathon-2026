from mcp.server.fastmcp import FastMCP
import joblib
import json
import os
from pathlib import Path
import pandas as pd
from pydantic import BaseModel
import httpx
import asyncio

# Initialize MCP Server
mcp = FastMCP("NYC-Reimbursement-Server")


class PredictionInput(BaseModel):
    features: list[float]


JSON_FILE_PATH = Path("../ml/models/delivery_charges_regression.json")


def load_json_model() -> dict:
    """Helper function to safely load the JSON file."""
    if not JSON_FILE_PATH.exists():
        # Return a fallback or mock model if file doesn't exist yet
        return {"error": "Model file not found", "data": {}}

    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}


# Load model (Global scope for the monolith)
# model = joblib.load("model.joblib")


@mcp.tool()
async def get_reimbursement_estimate(
    borough: str, facility_type: str, insurance_plan: str
) -> str:
    """Predicts likelihood of reimbursement for live birth in NYC private hospitals."""
    # input_data = pd.DataFrame([{
    #     'Borough': borough,
    #     'Hospital_Type': facility_type,
    #     'Payer': insurance_plan
    # }])

    # probability = model.predict_proba(input_data)[0][1]
    # return f"The estimated likelihood of full reimbursement is {probability:.2%}."
    model_data = load_json_model()
    result = "Prediction from JSON logic goes here."
    async with httpx.AsyncClient() as client:
        return result


if __name__ == "__main__":
    # Standard local initialization (defaults to stdio transport)
    mcp.run()
    # asyncio.run(main())
