import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from app.agent import Agent

from app.delivery_charges_regression_agent import DeliveryChargesRegressionAgent
from app.delivery_costs_regression_agent import DeliveryCostsRegressionAgent
from app.delivery_margin_diff_regression_agent import DeliveryMarginDiffRegressionAgent
from app.delivery_recovery_threshold_classification_agent import (
    DeliveryRecoveryThresholdClassificationRegressionAgent,
)
from app.model_prediction_tool import ModelPredictionTool


from dotenv import load_dotenv

from typing import Optional
import asyncio
import nest_asyncio
from app.llm_utils import llm_to_use


from typing import Dict, Any

# Load the .env file
load_dotenv()

# initialize io
nest_asyncio.apply()

import faulthandler

faulthandler.enable()

import json
import re


async def main():
    session_id = str(uuid.uuid4())

    core_query = """Show charges only for a person with race=white, length_of_stay=4, discharge_year=2023, age_group=30-49, apr_severity_of_illness_description=Minor and payment_typology_1="Blue Cross/Blue Shield."""

    core_query_2 = """Show charges, costs and cost differential projection for an expecting with race=Black/African American or Other Race, length_of_stay=4, discharge_year between 2021 to 2023, age_group=30-49, apr_severity_of_illness_description=Minor, payment_typology_1=Blue Cross/Blue Shield and hospital_county=Kings. Do not produce incomplete output, all values must have matching pair of brackets [] and curly brackets."""
    core_agent = Agent(session_id=session_id)

    query_charges = """Show charges only for a person with race=white, length_of_stay=4, discharge_year=2023, age_group=30-49, apr_severity_of_illness_description=Minor and payment_typology_1="Blue Cross/Blue Shield. If The tool is not accepting the patient profile parameters in the expected format, also return the parameters you are sending so a fix can be adjusted. Pm failure List and Share what tool you are using and how you are calling it. Do you call predict_from_model? You should if not what prompt do you require to use the tool that calls predict_from_model"""

    delivery_charges_regression_agent = DeliveryChargesRegressionAgent(llm=llm_to_use)
    delivery_costs_regression_agent = DeliveryCostsRegressionAgent(llm=llm_to_use)
    delivery_margin_diff_regression_agent = DeliveryMarginDiffRegressionAgent(
        llm=llm_to_use
    )
    delivery_rtc_agent = DeliveryRecoveryThresholdClassificationRegressionAgent(
        llm=llm_to_use
    )

    print("Performing a search for charges")
    response = await core_agent.chat(core_query_2)
    print(response)
    print("....................")
    # # content
    # print(response.response)
    # print("....................")
    # # print(str(response))
    # # print("....................")
    # print(str(response.response.content))
    # # json_data = response.raw.model_dump_json(indent=2)
    # # print(json_data)
    # print("....................")
    markdown_text = response.response.content
    clean_json_string = re.sub(
        r"^```json\s*|```$", "", markdown_text.strip(), flags=re.IGNORECASE
    )
    print(clean_json_string)
    print("....................")
    try:
        data = json.loads(clean_json_string)
    except Exception as e:
        print(
            f"content failes to render with error: {str(e)}. See \n{clean_json_string}"
        )
        print("....................")
        pattern = r'(?<=",[\s\n\r]\s*"table":\s*\[).*'
        # .*(?=.*\s*,[\n\r\s]*\s*['"]{1}table['"]\:)
        result = re.sub(pattern, "}", clean_json_string, flags=re.DOTALL)
        print(result)
        print("....................")
        data = json.loads(clean_json_string)

    print(data)
    print("....................")
    print(data["summary"])
    print("....................")

    # response_charges = await delivery_charges_regression_agent.chat(query_charges)
    # print(response_charges)

    model_prediction_tool = ModelPredictionTool(
        model_name="Testing Model name",
        json_model_filepath="ml/models/delivery_charges_regression.json",
        llm=llm_to_use,
    )

    basic_prompts = {
        "discharge_year": 2023,
        "length_of_stay": 4,
        "age_group30-49": 1,
        "raceWhite": 1,
        "apr_severity_of_illness_descriptionMinor": 1,
        "payment_typology_1Blue Cross/Blue Shield": 1,
    }
    # basic_prompts = {
    #     "discharge_year": 2026,
    #     "age_group": "30-49",
    #     "race": "Black/African American",
    #     "ethnicity": "Not Span/Hispanic",
    #     "length_of_stay": 5,
    #     "apr_severity_of_illness_description": "Minor",
    #     "type_of_admission": "Elective",
    #     "payment_typology_1": "Blue Cross/Blue Shield",
    #     "hospital_county": "Kings",
    #     "hospital_tier": "Private System"
    # }
    # response_from_prompts = model_prediction_tool.predict_from_model(basic_prompts)
    # print(response_from_prompts)


# Call the main async function
asyncio.run(main())
