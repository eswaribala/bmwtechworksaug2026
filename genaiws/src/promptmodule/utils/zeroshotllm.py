from dotenv import load_dotenv
import os
from google import genai
from openai import OpenAI   
env_path=os.path.join(os.path.dirname(__file__),'..', '.env')
load_dotenv(env_path)

#setup OpenAI client
#client = OpenAI(api_key=os.getenv("openai_ai_key"))

#use gemini llm
gemini_api_key=os.getenv("gemini_api_key")
client = genai.Client(api_key="AIzaSyD-GlttBbz-Y9GzqCcgk5FnOm_ACqm9qoQ")

zero_shot_prompt="""
Tata Nexon EV
Battery Electric Vehicle (BEV)
Battery Level= 5%
Temperature= 88°C
return only the classification
"""
'''
result=client.responses.create(
    model="gpt-4.1-mini",
    input=zero_shot_prompt
)
'''
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=zero_shot_prompt
)
print(response.text)



