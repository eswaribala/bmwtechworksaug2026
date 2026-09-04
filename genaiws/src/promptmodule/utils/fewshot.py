from dotenv import load_dotenv
import os
from google import genai
from openai import OpenAI   
env_path=os.path.join(os.path.dirname(__file__),'..','..','..', '.env')
load_dotenv(env_path)

#setup OpenAI client
client = OpenAI(api_key=os.getenv("openai_ai_key"))

#use gemini llm
#gemini_api_key=os.getenv("gemini_api_key")
#print(gemini_api_key)
#client = genai.Client(api_key=gemini_api_key)

few_shot_prompt="""
You are a BMW Support Assistant.

Classify each vehicle condition as:
EV Support,Infotainment Support,Mechanical Support

Example 1:
Battery: Not Charging
Classification: EV Support

Example 2:
Navigation: Not Working
Classification: Infotainment Support

Example 3:
AC: Not Working
Temperature: 115 C
Fault: AC not cooling
Classification: Mechanical Support

Now classify:

Battery percentage not increasing

Return only the classification.
"""
'''
result=client.responses.create(
    model="gpt-4.1-mini",
    input=few_shot_prompt
)
'''
response = client.responses.create(
    model="gpt-4.1-mini",
    input=few_shot_prompt
)
print(response)



