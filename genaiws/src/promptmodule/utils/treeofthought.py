from openai import OpenAI
import matplotlib.pyplot as plt

client = OpenAI()

# -------------------------------------------------
# 1. Ask LLM to analyze BMW vehicle
# -------------------------------------------------

prompt = """
You are a BMW vehicle diagnostic assistant.

Vehicle telemetry:
- Battery temperature: 58°C
- Vehicle speed: 110 km/h
- Cooling-fan status: Active
- Battery load: High
- Temperature sensor reading: Stable but unusually high
- Previous battery fault codes: None

Evaluate these three possible explanations.

Branch 1 - Cooling System Problem
Evaluate how strongly the telemetry supports this hypothesis.
Return: Low, Medium, or High.

Branch 2 - Sensor Problem
Evaluate how strongly the telemetry supports this hypothesis.
Return: Low, Medium, or High.

Branch 3 - High-Load Driving
Evaluate how strongly the telemetry supports this hypothesis.
Return: Low, Medium, or High.

Compare the three hypotheses and select the best-supported explanation.

Return ONLY this format:

Cooling System: <Low/Medium/High>
Sensor Problem: <Low/Medium/High>
High Load Driving: <Low/Medium/High>
Best-supported explanation: <Cooling System/Sensor Problem/High Load Driving>
"""

response = client.responses.create(
    model="gpt-5.6",
    input=prompt
)

result = response.output_text.strip()

print("\nLLM Diagnostic Result")
print("---------------------")
print(result)


# -------------------------------------------------
# 2. Extract best-supported explanation
# -------------------------------------------------

best_explanation = "Unknown"

for line in result.splitlines():
    if line.lower().startswith("best-supported explanation:"):
        best_explanation = line.split(":", 1)[1].strip()


# -------------------------------------------------
# 3. Generate hypothesis tree diagram
# -------------------------------------------------

fig, ax = plt.subplots(figsize=(14, 8))

ax.axis("off")

nodes = {
    "BMW Vehicle\nTelemetry": (0.50, 0.92),

    "Cooling System\nProblem": (0.20, 0.62),
    "Sensor\nProblem": (0.50, 0.62),
    "High-Load\nDriving": (0.80, 0.62),

    "Cooling Evidence\nTemp: 58°C\nFan: Active":
        (0.20, 0.38),

    "Sensor Evidence\nReading: Stable\nNo fault codes":
        (0.50, 0.38),

    "Load Evidence\nSpeed: 110 km/h\nBattery load: High":
        (0.80, 0.38),

    "Compare\nHypotheses": (0.50, 0.18),

    f"BEST SUPPORTED\n{best_explanation}":
        (0.50, 0.04)
}


# -------------------------------------------------
# Draw nodes
# -------------------------------------------------

for text, (x, y) in nodes.items():

    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=11,
        bbox=dict(
            boxstyle="round,pad=0.5",
            edgecolor="black",
            facecolor="white"
        )
    )


# -------------------------------------------------
# Arrow helper
# -------------------------------------------------

def arrow(start, end):

    x1, y1 = nodes[start]
    x2, y2 = nodes[end]

    ax.annotate(
        "",
        xy=(x2, y2 + 0.055),
        xytext=(x1, y1 - 0.055),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1.5
        )
    )


# -------------------------------------------------
# Telemetry → hypotheses
# -------------------------------------------------

arrow(
    "BMW Vehicle\nTelemetry",
    "Cooling System\nProblem"
)

arrow(
    "BMW Vehicle\nTelemetry",
    "Sensor\nProblem"
)

arrow(
    "BMW Vehicle\nTelemetry",
    "High-Load\nDriving"
)


# -------------------------------------------------
# Hypotheses → supporting evidence
# -------------------------------------------------

arrow(
    "Cooling System\nProblem",
    "Cooling Evidence\nTemp: 58°C\nFan: Active"
)

arrow(
    "Sensor\nProblem",
    "Sensor Evidence\nReading: Stable\nNo fault codes"
)

arrow(
    "High-Load\nDriving",
    "Load Evidence\nSpeed: 110 km/h\nBattery load: High"
)


# -------------------------------------------------
# Evidence → compare
# -------------------------------------------------

arrow(
    "Cooling Evidence\nTemp: 58°C\nFan: Active",
    "Compare\nHypotheses"
)

arrow(
    "Sensor Evidence\nReading: Stable\nNo fault codes",
    "Compare\nHypotheses"
)

arrow(
    "Load Evidence\nSpeed: 110 km/h\nBattery load: High",
    "Compare\nHypotheses"
)


# -------------------------------------------------
# Compare → final result
# -------------------------------------------------

arrow(
    "Compare\nHypotheses",
    f"BEST SUPPORTED\n{best_explanation}"
)


# -------------------------------------------------
# Title
# -------------------------------------------------

plt.title(
    "BMW Battery Overheating - Tree-Based Hypothesis Evaluation",
    fontsize=16
)

plt.savefig(
    "bmw_tree_of_thought.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()