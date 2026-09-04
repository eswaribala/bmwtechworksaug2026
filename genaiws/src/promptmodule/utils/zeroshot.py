from transformers import pipeline

zero_shot_classifier = pipeline("zero-shot-classification",
                                model="facebook/bart-large-mnli")

zero_shot_prompt="""
BMW Vehicle BMW i Series
Battery Electric Vehicle (BEV)
Battery Level= 20%
Temperature= 25°C
"""

labels =["Normal","Warning","Critical"]

result = zero_shot_classifier(zero_shot_prompt, candidate_labels=labels)
print(result)