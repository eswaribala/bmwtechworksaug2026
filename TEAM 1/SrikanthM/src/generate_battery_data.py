import csv
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(r"C:\Training\capstone project\src\datas")
VEHICLE_MASTER = BASE_DIR / "vehicle_master.csv"
TELEMETRY_PATH = BASE_DIR / "telemetry.csv"
CHARGING_PATH = BASE_DIR / "charging_sessions.csv"


def build_health_profile(index: int):
    if index <= 120:
        category = "Healthy"
        soh = 92 + ((index % 6) * 1.2) + (index % 3) * 0.5
    elif index <= 170:
        category = "Watch"
        soh = 84 + ((index % 8) * 1.1) + (index % 4) * 0.7
    else:
        category = "Critical"
        soh = 70 + ((index % 5) * 1.4) + (index % 3) * 0.8

    soh = round(max(68.0, min(98.0, soh)), 1)
    return category, soh


def write_telemetry():
    with VEHICLE_MASTER.open(newline="") as f:
        masters = list(csv.DictReader(f))

    rows = []
    for idx, master in enumerate(masters, start=1):
        category, soh = build_health_profile(idx)
        base_dt = datetime(2026, 1, 5) + timedelta(
            days=(idx - 1) // 5,
            hours=((idx - 1) % 5) * 2 + 8,
            minutes=(idx % 3) * 15,
        )

        soc = 35 + ((idx * 17) % 55)
        voltage = 370 + (idx % 18) + ((idx % 5) * 1.2)
        current = 12 + ((idx * 7) % 34)
        temp = 21 + ((idx * 3) % 12)
        speed = 20 + ((idx * 11) % 60)

        rows.append(
            {
                "Vehicle_ID": master["Vehicle_ID"],
                "Timestamp": base_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "SoC_Percent": soc,
                "SoH_Percent": soh,
                "Battery_Voltage_V": round(voltage + ((idx % 3) * 0.7), 1),
                "Battery_Current_A": round(current + ((idx % 4) * 0.8), 1),
                "Battery_Temperature_C": round(temp + ((idx % 4) * 0.7), 1),
                "Charging_Power_kW": 0,
                "Vehicle_Speed_kmh": speed,
                "Odometer_km": int(master["Odometer_km"]),
                "Health_Category": category,
            }
        )

    fieldnames = [
        "Vehicle_ID",
        "Timestamp",
        "SoC_Percent",
        "SoH_Percent",
        "Battery_Voltage_V",
        "Battery_Current_A",
        "Battery_Temperature_C",
        "Charging_Power_kW",
        "Vehicle_Speed_kmh",
        "Odometer_km",
        "Health_Category",
    ]

    with TELEMETRY_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows


def write_charging_sessions():
    with VEHICLE_MASTER.open(newline="") as f:
        masters = list(csv.DictReader(f))

    rows = []
    for idx, master in enumerate(masters, start=1):
        category, soh = build_health_profile(idx)
        start_dt = datetime(2026, 1, 5) + timedelta(
            days=(idx - 1) // 5,
            hours=((idx - 1) % 5) * 2 + 18,
            minutes=(idx % 4) * 10,
        )
        duration = 60 + (idx % 35)
        if category == "Healthy":
            initial_soc = 30 + (idx % 20)
            final_soc = 84 + (idx % 12)
            energy = 38 + (idx % 17)
            power = 27 + (idx % 12)
            interruptions = 0 if idx % 5 else 1
        elif category == "Watch":
            initial_soc = 35 + (idx % 25)
            final_soc = 77 + (idx % 10)
            energy = 31 + (idx % 15)
            power = 24 + (idx % 10)
            interruptions = 1 if idx % 3 else 2
        else:
            initial_soc = 42 + (idx % 18)
            final_soc = 72 + (idx % 8)
            energy = 25 + (idx % 12)
            power = 20 + (idx % 8)
            interruptions = 2 + (idx % 3)

        end_dt = start_dt + timedelta(minutes=duration)
        rows.append(
            {
                "Vehicle_ID": master["Vehicle_ID"],
                "Session_Start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "Session_End": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "Energy_Delivered_kWh": round(energy, 1),
                "Initial_SoC_Percent": initial_soc,
                "Final_SoC_Percent": final_soc,
                "Charging_Duration_Min": duration,
                "Charging_Power_kW": round(power + (soh / 30), 1),
                "Charging_Type": "DC_Fast" if idx % 3 == 0 else "AC",
                "Charging_Interruptions": interruptions,
                "Charger_Temperature_C": round(29 + (idx % 8) + (idx % 3) * 0.7, 1),
                "Environment_Temperature_C": round(21 + (idx % 6) * 1.2, 1),
                "Health_Category": category,
            }
        )

    fieldnames = [
        "Vehicle_ID",
        "Session_Start",
        "Session_End",
        "Energy_Delivered_kWh",
        "Initial_SoC_Percent",
        "Final_SoC_Percent",
        "Charging_Duration_Min",
        "Charging_Power_kW",
        "Charging_Type",
        "Charging_Interruptions",
        "Charger_Temperature_C",
        "Environment_Temperature_C",
        "Health_Category",
    ]

    with CHARGING_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows


if __name__ == "__main__":
    telemetry_rows = write_telemetry()
    charging_rows = write_charging_sessions()
    healthy = sum(1 for r in telemetry_rows if r["Health_Category"] == "Healthy")
    watch = sum(1 for r in telemetry_rows if r["Health_Category"] == "Watch")
    critical = sum(1 for r in telemetry_rows if r["Health_Category"] == "Critical")
    print(f"telemetry_rows={len(telemetry_rows)} healthy={healthy} watch={watch} critical={critical}")
    print(f"charging_rows={len(charging_rows)}")
