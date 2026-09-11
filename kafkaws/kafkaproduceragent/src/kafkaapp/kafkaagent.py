from pathlib import Path
import os
from functools import lru_cache
from dotenv import load_dotenv
from langchain_aws import ChatBedRockConverse

PROJECT_ROOT=Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

API_URL = os.getenv("TELEMETRY_API_URL")


@lru_cache(maxsize=1)
def get_agent_model():
  model=ChatBedRockConverse(
    model_id=os.environ["BEDROCK_MODEL_ID"],
    region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"),
    max_tokens=1024,
  ) 
  return model.bind_tools([publish_vehicle_telemetry])