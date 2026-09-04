from openai import OpenAI
import matplotlib.pyplot as plt

client = OpenAI()

# -------------------------------------------------
# 1. Ask LLM to analyze BMW vehicle
# -------------------------------------------------

prompt = """
You are a BMW vehicle diagnostic assistant.

Vehicle data:
Battery Level: 15%
Engine Temperature: 110°C
Fault Code: P0217

Analyze the following three branches:

Branch 1 - Battery:
Determine severity.

Branch 2 - Temperature:
Determine severity.

Branch 3 - Fault Code:
Determine severity.

Finally classify the overall vehicle condition as:
Normal, Warning, or Critical.

Return only this format:

Battery: Warning
Temperature: Critical
Fault: Critical
Final: Critical
"""

response = client.responses.create(
    model="gpt-5.6",
    input=prompt
)

result = response.output_text

print(result)

# -------------------------------------------------
# 2. Generate Tree-of-Thought diagram
# -------------------------------------------------

fig, ax = plt.subplots(figsize=(12, 7))

ax.axis("off")

# Node positions
nodes = {
    "BMW Vehicle\nTelemetry": (0.5, 0.90),

    "Battery\n15%": (0.20, 0.65),
    "Temperature\n110°C": (0.50, 0.65),
    "Fault Code\nP0217": (0.80, 0.65),

    "Warning": (0.20, 0.40),
    "Critical ": (0.50, 0.40),
    "Critical": (0.80, 0.40),

    "Compare\nBranches": (0.50, 0.20),

    "FINAL\nCRITICAL": (0.50, 0.05)
}

# Draw nodes
for text, (x, y) in nodes.items():

    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=12,
        bbox=dict(
            boxstyle="round,pad=0.5",
            edgecolor="black",
            facecolor="white"
        )
    )


# Function for arrows
def arrow(start, end):

    x1, y1 = nodes[start]
    x2, y2 = nodes[end]

    ax.annotate(
        "",
        xy=(x2, y2 + 0.04),
        xytext=(x1, y1 - 0.04),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1.5
        )
    )


# Root → branches
arrow(
    "BMW Vehicle\nTelemetry",
    "Battery\n15%"
)

arrow(
    "BMW Vehicle\nTelemetry",
    "Temperature\n110°C"
)

arrow(
    "BMW Vehicle\nTelemetry",
    "Fault Code\nP0217"
)


# Branch → result
arrow(
    "Battery\n15%",
    "Warning"
)

arrow(
    "Temperature\n110°C",
    "Critical "
)

arrow(
    "Fault Code\nP0217",
    "Critical"
)


# Results → comparison
arrow(
    "Warning",
    "Compare\nBranches"
)

arrow(
    "Critical ",
    "Compare\nBranches"
)

arrow(
    "Critical",
    "Compare\nBranches"
)


# Comparison → final result
arrow(
    "Compare\nBranches",
    "FINAL\nCRITICAL"
)


plt.title(
    "BMW Vehicle Diagnostic - Tree of Thought",
    fontsize=16
)

plt.savefig(
    "bmw_tree_of_thought.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()