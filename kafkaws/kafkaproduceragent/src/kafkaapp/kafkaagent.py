from pathlib import Path
import os

from httpcore2 import request
from urllib import error, request, response
from kafkaapp.schemas import SalesRequest
from functools import lru_cache
from dotenv import load_dotenv
from langchain_core import tool
from kafkaapp.schemas import SalesRequest
from langchain_aws import ChatBedRockConverse

PROJECT_ROOT=Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

API_URL = os.getenv("TELEMETRY_API_URL")

@tool(args_schema=SalesRequest)
def publish_sales_data(sales_data):
      try:
         response= request.post(f"{API_URL}/publish_sales_data", json=sales_data)
      except request.RequestException as e:
          return {
                "status" : "unconfirmed",
                "message" : (
                    "No API response was received. Delivery is unknown. "
                    "Retrying could duplicate the event."
                ),
                }

      try:
          result=response.json()
      except ValueError as e:
          return {
              "status": "unconfirmed",
              "message": (
                  "Failed to parse API response. Delivery is unknown. "
                  "Retrying could duplicate the event."
              ),
          }

      if(result.status_code==201 and isinstance(result, dict) and result.get("status") == "delivered"):
          return {
              "status": "confirmed",
              "message": "Sales data successfully delivered."
          }
      else:
          return {
              "status": "unconfirmed",
              "message": "Sales data delivery failed or is unknown."
          }

@lru_cache(maxsize=1)
def get_agent_model():
  model=ChatBedRockConverse(
    model_id=os.environ["BEDROCK_MODEL_ID"],
    region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"),
    max_tokens=1024,
  ) 
  return model.bind_tools([publish_sales_data])