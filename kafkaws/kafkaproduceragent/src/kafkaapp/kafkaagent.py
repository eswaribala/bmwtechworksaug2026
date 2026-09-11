from pathlib import Path
import os

import requests
from urllib import error, response

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic_core import ValidationError
from kafkaapp.schemas import SalesRequest
from functools import lru_cache
from dotenv import load_dotenv
from langchain_core.tools import tool
from kafkaapp.schemas import SalesRequest
from langchain_aws import  ChatBedrockConverse

PROJECT_ROOT=Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

API_URL = os.getenv("SALES_API_URL")

@tool(args_schema=SalesRequest)
def publish_sales_data(  product_id: int,
    quantity: int,
    price: float,
    total: float,
    region: str,)->dict:
    """Publish one vehicle telemetry event through the Kafka producer API."""
    payload={
          "product_id": product_id,
          "quantity": quantity,
          "price": price,
          "total": total,
          "region": region,
    }
    try:
         response= requests.post(f"{API_URL}/publish_sales_data", json=payload)
    except requests.RequestException as e:
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

    if(response.status_code==201 and isinstance(result, dict) and result.get("status") == "delivered"):
          return result
    else:
          return {
              "status": "unconfirmed",
              "message": "Sales data delivery failed or is unknown."
          }

@lru_cache(maxsize=1)
def get_agent_model():
  model=ChatBedrockConverse(
    model_id=os.environ["BEDROCK_MODEL_ID"],
    region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"),
    max_tokens=1024,
  ) 
  return model.bind_tools([publish_sales_data])


SYSTEM_PROMPT="""You are a BMW sales assistant.
 Use publish_sales_data only when the user 
 requests publishing or sending sales data.
  Rules:
  1. Handle exactly one sales data entry per request.
  2. Require product_id, quantity, price, total and region.
  3. Never invent missing values.
  4. If values are missing, ask for a complete request containing all fields.
  5. quantity, price, total must be nonnegative.
  6. Call the tool once when all required values are available.
  7. Do not claim delivery yourself; the application returns the API receipt.
  8. Ensure all numeric values are valid before calling the tool.  
  """

def run_agent(message:str):
    reply=get_agent_model().invoke(
         [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=message),
         ]
     )
     # The model may ask for missing information instead of calling a tool.
    if not reply.tool_calls:
            return {
                "status": "not_published",
                "answer": reply.content,
            }

        # Validate every proposed action before executing anything.
    if len(reply.tool_calls) != 1:
            return {
                "status": "not_published",
                "answer": "Please submit exactly one product per request.",
            }

    call = reply.tool_calls[0]

    if call["name"] != publish_sales_data.name:
            return {
                "status": "not_published",
                "answer": "Unsupported tool.",
            }

    try:
            arguments = SalesRequest.model_validate(call["args"])
    except ValidationError as error:
            return {
                "status": "not_published",
                "answer": f"Invalid sales data: {error}",
            }

        # Execute once and return the actual receipt without an LLM rewrite.
    return publish_sales_data.invoke(arguments.model_dump())

        