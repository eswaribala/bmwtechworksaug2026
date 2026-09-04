from transformers import pipeline

zero_shot_classifier = pipeline("zero-shot-classification",
                                model="facebook/bart-large-mnli")

zero_shot_prompt="""
Tata Nexon EV
Battery Electric Vehicle (BEV)
Battery Level= 5%
Temperature= 88°C
"""

labels =["Normal","Warning","Critical"]

result = zero_shot_classifier(zero_shot_prompt, candidate_labels=labels)
print(result)