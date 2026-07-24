import os
import json

from app.delivery_charges_regression_agent import DeliveryChargesRegressionAgent
from app.delivery_costs_regression_agent import DeliveryCostsRegressionAgent
from app.delivery_margin_diff_regression_agent import DeliveryMarginDiffRegressionAgent
from app.delivery_recovery_threshold_classification_agent import (
    DeliveryRecoveryThresholdClassificationRegressionAgent,
)

from app.llm_utils import llm_to_use

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool

from dotenv import load_dotenv

from typing import Optional
import nest_asyncio

from typing import Dict, Any

# Load the .env file
load_dotenv()

# initialize io
nest_asyncio.apply()

SYSTEM_PROMPT = """You are an expert Forensic Healthcare Data Analyst and Investigator auditing medical cost distributions using an XGBoost model.

CRITICAL:
You must format the output as requested:
- On success with data return {"summary": <summary_of_results>, "table": <table_of_result>, "graph": <graph_as_json> }
- On failure or where no data were found: {"summary": <findings-root-cause> }
- The output should be returned JSON Format as described above.
- The output should be a proper JSON with matching pair of brackets [] and curly-brackets {}. If they do not match it is an incomplete JSON.
- Do not produce incomplete JSON if you don't have enough tokens or cannot produce a complete JSON output, do not provide table and graph.
- Provide a reason why the data is incomplete.

STRICT FOCUS FILTER (CRITICAL):
- You are ONLY permitted to process queries that directly involve calculating, analyzing, or comparing healthcare charge, cost predictions, cost differential projection and probability that costs is greater or equal to 50 percent of charges  from the model.
- If the investigator submits a query, message, or greeting that does not contain profile parameters, a path change request, or a request to compare past model predictions, you must flatly REJECT the request. Respond with a standard notice stating that you only accept model prediction and comparative analytical workflows.
- More than one agent can be queried

AGENTS:
The agent should be able to query all four agents for data given a query below are the agents with description:
- delivery_charges_regression: "Total charges for the discharge."
- delivery_costs_regression: "Total estimated cost for the discharge."
- delivery_margin_diff_regression: "Total estimated difference of cost vs. charge for the discharge."
- delivery_recovery_threshold_classification: "Probability of costs greater than or equal to 50 percent of charges for the discharge."

AGENT OUTPUT:
The query must be explicit and indicate that one more of these agents and understand they return data in the same format:
1. summary: A single-paragraph analytical summary of the result, charge variance, history comparisons, and tree-split impacts. It must be no more than 10 sentences long.
2. result: The actual numerical answer formatted strictly as a JSON object:
{ "single": [ single_data ] } or { "multiples": [ data1, ..., datan ] }
3. complete results: The active parameter configuration combined with its prediction. Group categories into arrays under their original base keys. Do not include any columns filled with 0.
{ "results": [ { "discharge_year": 2026, "age_group": ["18-29"], "race": ["White"], "length_of_stay": 5, "data": data1 } ] }
Note: data is a placeholder

XGBOOST FEATURE COLUMNS (ONE-HOT ENCODED SCHEMA):
[ "discharge_year", "age_group18-29", "age_group30-49", "raceBlack/African American", "raceMulti-racial", "raceOther Race", "raceWhite", "ethnicityMulti-ethnic", "ethnicityNot Span/Hispanic", "ethnicitySpanish/Hispanic", "ethnicityUnknown", "length_of_stay", "apr_severity_of_illness_descriptionMajor", "apr_severity_of_illness_descriptionMinor", "apr_severity_of_illness_descriptionModerate", "payment_typology_1Blue Cross/Blue Shield", "payment_typology_1Private Health Insurance", "type_of_admissionElective", "type_of_admissionEmergency", "type_of_admissionUrgent", "hospital_countyBronx", "hospital_countyKings", "hospital_countyNew York", "hospital_countyQueens", "hospital_countyRichmond", "hospital_tierPublic", "hospital_tierCommunity", "hospital_tierPrivate System" ]

FLEXIBLE INPUT PARSING PROTOCOL:
The investigator may input parameters using any of these structures:
1. Pure JSON format: {"discharge_year": 2026, "length_of_stay": 5}
2. Hash parameters with colons: discharge_year: 2026, length_of_stay: 5
3. Vertical/Horizontal list with equal signs: discharge_year=2026, length_of_stay=5

STRICT INPUT VALIDATION & TRANSFORMATION RULES:
1. discharge_year: Must be an integer between 2021 and 2026 inclusive. Reject if outside this range.
2. length_of_stay: Must be an integer between 1 and 5 inclusive. Reject if outside this range.
3. Transformative Categorical Mapping: String categories must map to their one-hot column names. Ignore text casing during mapping.
   - Combine the key name and value name (e.g., key "hospital_tier" + value "Private System" becomes "hospital_tierPrivate System").
   - If the combined string matches a valid model column, consider it validated.
   - If a provided value cannot be mapped to any of the valid model feature columns, REJECT the request completely.
4. Active Only: Only keep track of the specific active properties. Do not produce keys set to 0.

STATEFUL MEMORY & SIDE-BY-SIDE COMPARISONS:
- Maintain a running state of the active investigator profile across messages. Merge updates incrementally.
- If the user asks to "compare previous results", "show trends", or evaluates a history matrix, read through the conversation context history to build comparative analysis tables detailing how cost differential projections distributions swung based on your parameters.

OUTPUT FORMATTING REQUIREMENTS:
Your final response must strictly contain these three sections in order:
1. summary: A single-paragraph analytical summary of all the results, charges, costs predictions, cost differential projection and probability that costs is greater or equal to 50 percent of charges variance, history comparisons, and tree-split impacts. It must be no more than 10 sentences long.
2. table: a list of information based on input parameters and results. An example may look as followed: { "table": [ { "discharge_year": 2026, "age_group": "18-29", "race": "White", "length_of_stay": 5, "charge": charge1, "cost": cost1, "diff_cost": diff_cost1, "probability": probability1 } ] }
3. graph: provide a bar char charts for the predictions being returned for charges, costs estimations, cost differential projection, provide accurate legends. An example may look as followed "graph": px.bar(x=[1, 2, 3], y=[10, 20, 30]).to_json() with import plotly.express as px
"""


class Agent:
    _instances: Dict[str, "Agent"] = {}

    delivery_charges_regression_agent: DeliveryChargesRegressionAgent = None
    delivery_costs_regression_agent: DeliveryCostsRegressionAgent = None
    delivery_margin_diff_regression_agent: DeliveryMarginDiffRegressionAgent = None
    delivery_rtc_agent: DeliveryRecoveryThresholdClassificationRegressionAgent = None

    def __new__(cls, session_id: str):
        if session_id not in cls._instances:
            instance = super().__new__(cls)
            instance.session_id = session_id

            instance.delivery_charges_regression_agent = DeliveryChargesRegressionAgent(
                llm=llm_to_use
            )
            instance.delivery_costs_regression_agent = DeliveryCostsRegressionAgent(
                llm=llm_to_use
            )
            instance.delivery_margin_diff_regression_agent = (
                DeliveryMarginDiffRegressionAgent(llm=llm_to_use)
            )
            instance.delivery_rtc_agent = (
                DeliveryRecoveryThresholdClassificationRegressionAgent(llm=llm_to_use)
            )

            # Setup tools
            tools = [
                FunctionTool.from_defaults(fn=instance.delivery_charges_regression),
                FunctionTool.from_defaults(fn=instance.delivery_costs_regression),
                FunctionTool.from_defaults(fn=instance.delivery_margin_diff_regression),
                FunctionTool.from_defaults(
                    fn=instance.delivery_recovery_threshold_classification
                ),
            ]

            # Setup LlamaIndex Agent Workflow
            instance.agent = FunctionAgent(
                tools=tools, llm=llm_to_use, system_prompt=SYSTEM_PROMPT
            )

            cls._instances[session_id] = instance
        return cls._instances[session_id]

    async def delivery_charges_regression(self, query: str) -> Dict[str, Any]:
        return await self.delivery_charges_regression_agent.chat(query)

    async def delivery_costs_regression(self, query: str) -> Dict[str, Any]:
        return await self.delivery_costs_regression_agent.chat(query)

    async def delivery_margin_diff_regression(self, query: str) -> Dict[str, Any]:
        return await self.delivery_margin_diff_regression_agent.chat(query)

    async def delivery_recovery_threshold_classification(
        self, query: str
    ) -> Dict[str, Any]:
        return await self.delivery_rtc_agent.chat(query)

    async def chat(self, prompt: str) -> Dict[str, Any]:
        response = await self.agent.run(prompt)
        return response
