from openai import OpenAI

client = OpenAI()

vehicle_data = """
Vehicle: BMW i4
Battery Level: 15%
Temperature: 110°C
Fault Code: P0217
Speed: 80 km/h
"""

# -------------------------------------------------
# PROMPT 1
# Extract important vehicle observations
# -------------------------------------------------

prompt1 = f"""
You are a BMW vehicle diagnostic assistant.

Analyze the following vehicle telemetry.

{vehicle_data}

Identify only the important diagnostic observations.

Return the observations as short bullet points.
"""

response1 = client.responses.create(
    model="gpt-5.6",
    input=prompt1
)

observations = response1.output_text

print("STEP 1 - OBSERVATIONS")
print(observations)


# -------------------------------------------------
# PROMPT 2
# Classify severity using output from Prompt 1
# -------------------------------------------------

prompt2 = f"""
You are a BMW vehicle safety analyst.

The diagnostic assistant produced these observations:

{observations}

Based on these observations, classify the vehicle condition as:

Normal
Warning
Critical

Return:

Classification:
Reason:
"""

response2 = client.responses.create(
    model="gpt-5.6",
    input=prompt2
)

classification = response2.output_text

print("\nSTEP 2 - CLASSIFICATION")
print(classification)


# -------------------------------------------------
# PROMPT 3
# Generate recommended action
# -------------------------------------------------

prompt3 = f"""
You are a BMW service advisor.

Vehicle diagnostic result:

{classification}

Original vehicle information:

{vehicle_data}

Provide a concise recommended action for the driver.

Return:

Action:
Priority:
"""

response3 = client.responses.create(
    model="gpt-5.6",
    input=prompt3
)

recommendation = response3.output_text

print("\nSTEP 3 - RECOMMENDATION")
print(recommendation)