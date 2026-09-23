# Battery Health Calculations

This document explains the mathematical calculations used by the PySpark
pipeline in simple terms. The calculations are performed for each vehicle
using `Vehicle_ID` as the grouping key.

## 1. What the Pipeline Measures

For every vehicle, the pipeline combines three datasets:

- **Telemetry:** battery readings over time
- **Vehicle master:** model, region, age, battery capacity, and odometer
- **Charging sessions:** charging count, energy, power, duration, and interruptions

The main health measurements are:

1. Average state of charge (SoC)
2. Average state of health (SoH)
3. Minimum and maximum SoH
4. SoH variability
5. Initial and latest SoH
6. SoH change over time
7. Charging behavior
8. Final health category and score

## 2. Average Battery Level

### Meaning

`SoC_Percent` describes how full the battery is during a telemetry reading.
The pipeline calculates the average SoC for each vehicle.

### Formula

$$
Average\ SoC = \frac{SoC_1 + SoC_2 + ... + SoC_n}{n}
$$

### Example

If one vehicle has SoC readings of `40`, `60`, and `80`:

```text
Average SoC = (40 + 60 + 80) / 3
            = 60%
```

### PySpark

```python
F.avg("SoC_Percent").alias("avg_battery_level")
```

This metric describes normal battery usage. It does not directly determine
whether the battery is Healthy, Watch, or Critical.

## 3. Average State of Health

### Meaning

`SoH_Percent` estimates the battery's remaining capability compared with a
healthy or new battery. This is the main value used for classification.

### Formula

$$
Average\ SoH = \frac{SoH_1 + SoH_2 + ... + SoH_n}{n}
$$

### Example

If a vehicle has SoH readings of `94`, `92`, and `93`:

```text
Average SoH = (94 + 92 + 93) / 3
            = 93%
```

### PySpark

```python
F.avg("SoH_Percent").alias("avg_soh")
```

Using an average prevents one unusual reading from deciding the entire
vehicle classification.

## 4. Minimum, Maximum, and SoH Variation

The pipeline also calculates the range and variation of SoH readings.

```python
F.min("SoH_Percent").alias("min_soh")
F.max("SoH_Percent").alias("max_soh")
F.stddev("SoH_Percent").alias("soh_stddev")
```

### Minimum and maximum

```text
min_soh = lowest observed SoH reading
max_soh = highest observed SoH reading
```

### Standard deviation

Standard deviation shows how widely the readings vary around the average.

- A small value means the readings are consistent.
- A large value means the readings fluctuate more.

The current classification rules use `avg_soh`, not `soh_stddev`, but the
variation is saved for analysis and dashboard use.

## 5. Initial and Latest SoH

The pipeline sorts telemetry by `Vehicle_ID` and `Timestamp` before calculating
the first and last SoH values.

```python
telemetry_df.orderBy("Vehicle_ID", "Timestamp")
```

For each vehicle:

```text
initial_soh = first SoH reading in time order
latest_soh  = last SoH reading in time order
```

### Example

```text
First reading: 95%
Last reading:  88%

initial_soh = 95
latest_soh  = 88
```

These values provide a simple view of how the battery changed over the
observed period.

## 6. SoH Change

The code calculates the absolute SoH change as:

$$
SoH\ Change = Latest\ SoH - Initial\ SoH
$$

In the output this field is called `soh_drop`.

### Example: battery health declined

```text
initial_soh = 95
latest_soh  = 88

soh_drop = 88 - 95
         = -7 percentage points
```

A negative result means the latest SoH is lower than the initial SoH.

### Example: battery health increased

```text
initial_soh = 88
latest_soh  = 92

soh_drop = 92 - 88
         = 4 percentage points
```

A positive result means the latest SoH is higher than the initial SoH.

### PySpark

```python
(F.last("SoH_Percent") - F.first("SoH_Percent")).alias("soh_drop")
```

## 7. Percentage SoH Change

The pipeline calculates percentage change using the initial SoH as the
baseline.

$$
Percent\ Change =
\frac{Latest\ SoH - Initial\ SoH}{Initial\ SoH} \times 100
$$

The output field is called `percent_drop`.

### Example: battery health declined

```text
initial_soh = 95
latest_soh  = 88

percent_drop = ((88 - 95) / 95) * 100
             = -7.37%
```

This means the latest SoH is approximately 7.37% lower than the initial SoH.

### PySpark

```python
(
    (F.last("SoH_Percent") - F.first("SoH_Percent"))
    / F.first("SoH_Percent")
    * 100
).alias("percent_drop")
```

## 8. Important Sign Convention

The current code calculates:

```text
percent_drop = (latest_soh - initial_soh) / initial_soh * 100
```

Therefore:

| Result | Meaning |
|---:|---|
| Negative | SoH declined |
| Zero | SoH stayed the same |
| Positive | SoH increased |

A mathematically named `percent_drop` is usually expected to be positive when
health declines. That alternative formula would be:

$$
Percent\ Drop\ (positive\ form) =
\frac{Initial\ SoH - Latest\ SoH}{Initial\ SoH} \times 100
$$

For the same example:

```text
positive percent drop = ((95 - 88) / 95) * 100
                     = 7.37%
```

The current implementation has not switched to this positive form. This is
important when interpreting thresholds.

## 9. Charging Calculations

Charging metrics are grouped by `Vehicle_ID`.

### Charging frequency

```python
F.count("*").alias("charging_frequency")
```

Formula:

```text
Charging frequency = number of charging sessions for the vehicle
```

### Average energy delivered

```python
F.avg("Energy_Delivered_kWh").alias("avg_energy_delivered_kwh")
```

Formula:

$$
Average\ Energy =
\frac{Energy_1 + Energy_2 + ... + Energy_n}{n}
$$

### Average charging power

```python
F.avg("Charging_Power_kW").alias("avg_charging_power_kw")
```

### Average charging duration

```python
F.avg("Charging_Duration_Min").alias("avg_charging_duration_min")
```

### Charging interruptions

The pipeline counts sessions where interruptions are greater than zero:

```python
F.sum(
    F.when(F.col("Charging_Interruptions") > 0, 1).otherwise(0)
).alias("charging_interruptions_count")
```

Example:

```text
Sessions:       0, 1, 2, 0, 3
Interrupted?:   No, Yes, Yes, No, Yes
Count:          3 interrupted sessions
```

These charging values are included in the curated output. The current health
classification itself is based on `avg_soh` and the subsequent `percent_drop`
override checks.

## 10. Health Thresholds

The first classification uses the average SoH for each vehicle.

### Rule table

| Average SoH | Category | Score |
|---:|---|---:|
| `90` or higher | Healthy | 100 |
| `80` to less than `90` | Watch | 70 |
| Less than `80` | Critical | 40 |

### Plain-language interpretation

- **Healthy:** The battery retains at least 90% average health.
- **Watch:** The battery is between 80% and 90% average health.
- **Critical:** The battery is below 80% average health.

### PySpark implementation

```python
F.when(F.col("avg_soh") >= 90, "Healthy")
 .when(F.col("avg_soh") >= 80, "Watch")
 .otherwise("Critical")
```

Because the conditions are evaluated from top to bottom:

```text
avg_soh = 95 -> Healthy
avg_soh = 90 -> Healthy
avg_soh = 89 -> Watch
avg_soh = 80 -> Watch
avg_soh = 79 -> Critical
```

The score uses the same boundaries:

```python
F.when(F.col("avg_soh") >= 90, 100)
 .when(F.col("avg_soh") >= 80, 70)
 .otherwise(40)
```

## 11. Degradation Override Rules

After the initial SoH classification, the pipeline applies additional category
conditions:

```python
Healthy + percent_drop > 10 -> Watch
Watch   + percent_drop > 15 -> Critical
```

The current code is equivalent to:

```python
F.when(
    (F.col("battery_health_category") == "Healthy")
    & (F.col("percent_drop") > 10),
    "Watch",
)
.when(
    (F.col("battery_health_category") == "Watch")
    & (F.col("percent_drop") > 15),
    "Critical",
)
```

### Important interpretation

Because the current `percent_drop` formula is `latest - initial`, a declining
battery produces a negative value. For example, a change from 95% to 80%
produces `-15.79%`, not `+15.79%`.

Therefore, the current checks `> 10` and `> 15` trigger when SoH increases by
more than those percentages. If the business requirement is to promote a
vehicle when its health **declines** beyond a threshold, the comparison should
use the negative direction, for example:

```python
Healthy + percent_drop < -10 -> Watch
Watch   + percent_drop < -15 -> Critical
```

Or the code can use the positive drop formula:

```python
positive_drop = (initial_soh - latest_soh) / initial_soh * 100

Healthy + positive_drop > 10 -> Watch
Watch   + positive_drop > 15 -> Critical
```

The architecture currently preserves the existing implementation. This section
makes the sign issue visible so the threshold decision can be changed
intentionally.

## 12. Complete Worked Example

Assume one vehicle has these telemetry readings:

```text
SoH readings: 95, 92, 88
SoC readings: 40, 60, 80
```

### Step 1: Average SoC

```text
avg_battery_level = (40 + 60 + 80) / 3
                  = 60%
```

### Step 2: Average SoH

```text
avg_soh = (95 + 92 + 88) / 3
        = 91.67%
```

### Step 3: Initial and latest SoH

```text
initial_soh = 95%
latest_soh  = 88%
```

### Step 4: Absolute change

```text
soh_drop = 88 - 95
         = -7 percentage points
```

### Step 5: Percentage change

```text
percent_drop = ((88 - 95) / 95) * 100
             = -7.37%
```

### Step 6: Initial classification

```text
avg_soh = 91.67%
91.67 >= 90

Category = Healthy
Score    = 100
```

### Step 7: Override check

```text
Healthy and percent_drop > 10
Healthy and -7.37 > 10
False
```

### Final current result

```text
battery_health_category = Healthy
health_score            = 100
```

Under a positive-decline formula, this vehicle would have a 7.37% decline,
which is still below the 10% Healthy-to-Watch threshold.

## 13. Calculation Order in PySpark

The calculation order is:

```text
1. Read the three CSV files
2. Parse timestamps and cast numeric columns
3. Remove rows missing required fields
4. Group telemetry by Vehicle_ID
5. Calculate average and summary SoH metrics
6. Sort telemetry and calculate initial/latest SoH
7. Calculate SoH change and percentage change
8. Group charging sessions by Vehicle_ID
9. Join telemetry metrics, vehicle master, charging metrics, and degradation metrics
10. Assign the initial category and score from avg_soh
11. Apply degradation override rules
12. Write the final result as partitioned Parquet
```

The final output fields used by the calculations are:

```text
avg_battery_level
avg_soh
min_soh
max_soh
soh_stddev
initial_soh
latest_soh
soh_drop
percent_drop
charging_frequency
avg_energy_delivered_kwh
avg_charging_power_kw
avg_charging_duration_min
charging_interruptions_count
battery_health_category
health_score
```

## 14. Summary

The most important calculation is the average SoH threshold:

```text
90% or higher -> Healthy
80% to below 90% -> Watch
below 80% -> Critical
```

The pipeline also calculates how SoH changed over time. When using the current
formula, remember that a decline is negative. Any future degradation threshold
must either compare `percent_drop` with a negative limit or change the formula
to return a positive value for a decline.
