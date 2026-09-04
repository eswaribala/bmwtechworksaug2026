from dotenv import load_dotenv
import os
from google import genai
from openai import OpenAI   
env_path=os.path.join(os.path.dirname(__file__),'..', '.env')
load_dotenv(env_path)

#setup OpenAI client
client = OpenAI(api_key=os.getenv("openai_ai_key"))

#use gemini llm
gemini_api_key=os.getenv("gemini_api_key")
client = genai.Client(api_key=gemini_api_key)



