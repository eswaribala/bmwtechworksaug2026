from dotenv import load_dotenv
import os
from openai import OpenAI   
env_path=os.path.join(os.path.dirname(__file__),'..', '.env')
load_dotenv(env_path)

#setup OpenAI client
client = OpenAI(api_key=os.getenv("openai_ai_key"))

#test the client



