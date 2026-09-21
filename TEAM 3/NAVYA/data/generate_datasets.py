import csv
import random
from datetime import date, timedelta
from pathlib import Path


# ============================================================
# BMW ENTERPRISE BATCH ETL - DATASET GENERATOR
# ============================================================

# The script is inside the project's data folder.
PROJECT_ROOT = Path(__file__).resolve().parent

# CSV files will be created inside data/sample
OUTPUT_DIR = PROJECT_ROOT / "sample"

# Create output folder if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Makes the generated data reproducible
random.seed(42)


# ============================================================
# MASTER DATA
# ============================================================

MODELS = [
    "BMW 3 Series",
    "BMW 5 Series",
    "BMW X1",
    "BMW X3",
    "BMW X5",
    "BMW i4",
    "BMW iX",
    "BMW 7 Series",
    "BMW X7",
    "BMW 2 Series",
]


FUEL_BY_MODEL = {
    "BMW i4": "Electric",
    "BMW iX": "Electric",
    "BMW 3 Series": "Petrol",
    "BMW 5 Series": "Diesel",
    "BMW X1": "Petrol",
    "BMW X3": "Diesel",
    "BMW X5": "Diesel",
    "BMW 7 Series": "Hybrid",
    "BMW X7": "Petrol",
    "BMW 2 Series": "Petrol",
}


REGIONS = [
    "North",
    "South",
    "East",
    "West",
]


CITIES = {
    "North": [
        "Delhi",
        "Chandigarh",
        "Jaipur",
    ],
    "South": [
        "Chennai",
        "Bengaluru",
        "Hyderabad",
    ],
    "East": [
        "Kolkata",
        "Bhubaneswar",
        "Patna",
    ],
    "West": [
        "Mumbai",
        "Pune",
        "Ahmedabad",
    ],
}


SERVICE_TYPES = [
    "Routine Service",
    "Oil Change",
    "Brake Service",
    "Battery Check",
    "Inspection",
    "Repair",
]


FAILURE_CODES = [
    "NONE",
    "BRK01",
    "BAT01",
    "ENG01",
    "ELEC01",
]


# ============================================================
# HELPER FUNCTION
# ============================================================

def random_date(start_date, end_date):
    """Generate a random date between two dates."""

    days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, days)
    )


# ============================================================
# 1. DEALER DATASET
# ============================================================

def generate_dealers():
    dealers = []

    for i in range(1, 101):

        dealer_id = f"D{i:03d}"

        region = random.choice(REGIONS)

        city = random.choice(CITIES[region])

        dealer = {
            "dealer_id": dealer_id,
            "dealer_name": f"BMW Dealer {i}",
            "city": city,
            "region": region,
            "capacity": random.randint(50, 300),
            "rating": round(random.uniform(3.0, 5.0), 1),
        }

        dealers.append(dealer)

    # --------------------------------------------------------
    # Intentional data-quality issues
    # --------------------------------------------------------

    # Duplicate dealer ID
    dealers[10]["dealer_id"] = dealers[9]["dealer_id"]

    # Missing region
    dealers[20]["region"] = ""

    # Invalid rating
    dealers[30]["rating"] = 8.5

    return dealers


# ============================================================
# 2. VEHICLE MASTER DATASET
# ============================================================

def generate_vehicles():

    vehicles = []

    start_date = date(2018, 1, 1)
    end_date = date(2025, 12, 31)

    for i in range(1, 1001):

        vehicle_id = f"BMWV{i:05d}"

        model = random.choice(MODELS)

        vehicle = {
            "vehicle_id": vehicle_id,
            "vin": f"WBA{i:014d}",
            "model": model,
            "model_year": random.randint(2020, 2025),
            "fuel_type": FUEL_BY_MODEL[model],
            "region": random.choice(REGIONS),
            "manufacturing_date": random_date(
                start_date,
                end_date
            ).isoformat(),
        }

        vehicles.append(vehicle)

    # --------------------------------------------------------
    # Intentional data-quality issues
    # --------------------------------------------------------

    # Missing vehicle ID
    vehicles[50]["vehicle_id"] = ""

    # Duplicate vehicle ID
    vehicles[100]["vehicle_id"] = vehicles[99]["vehicle_id"]

    # Invalid model year
    vehicles[150]["model_year"] = 1900

    return vehicles


# ============================================================
# 3. SALES DATASET
# ============================================================

def generate_sales(vehicles, dealers):

    sales = []

    start_date = date(2024, 1, 1)
    end_date = date(2026, 8, 31)

    valid_vehicles = [
        vehicle
        for vehicle in vehicles
        if vehicle["vehicle_id"]
    ]

    valid_dealers = [
        dealer
        for dealer in dealers
        if dealer["dealer_id"]
    ]

    for i in range(1, 1001):

        vehicle = random.choice(valid_vehicles)

        dealer = random.choice(valid_dealers)

        sale = {
            "sale_id": f"S{i:05d}",
            "vehicle_id": vehicle["vehicle_id"],
            "dealer_id": dealer["dealer_id"],
            "customer_id": f"C{random.randint(1, 1000):04d}",
            "sale_date": random_date(
                start_date,
                end_date
            ).isoformat(),
            "model": vehicle["model"],
            "region": dealer["region"],
            "price": round(
                random.uniform(35000, 150000),
                2
            ),
            "quantity": random.randint(1, 3),
        }

        sales.append(sale)

    # --------------------------------------------------------
    # Intentional data-quality issues
    # --------------------------------------------------------

    # Duplicate sale ID
    sales[20]["sale_id"] = sales[19]["sale_id"]

    # Missing vehicle ID
    sales[40]["vehicle_id"] = ""

    # Negative price
    sales[60]["price"] = -5000

    # Invalid sale date
    sales[80]["sale_date"] = "not-a-date"

    return sales


# ============================================================
# 4. MAINTENANCE DATASET
# ============================================================

def generate_maintenance(vehicles, dealers):

    maintenance = []

    start_date = date(2024, 1, 1)
    end_date = date(2026, 8, 31)

    valid_vehicles = [
        vehicle
        for vehicle in vehicles
        if vehicle["vehicle_id"]
    ]

    valid_dealers = [
        dealer
        for dealer in dealers
        if dealer["dealer_id"]
    ]

    for i in range(1, 1001):

        vehicle = random.choice(valid_vehicles)

        dealer = random.choice(valid_dealers)

        maintenance_record = {
            "service_id": f"SRV{i:05d}",
            "vehicle_id": vehicle["vehicle_id"],
            "dealer_id": dealer["dealer_id"],
            "service_date": random_date(
                start_date,
                end_date
            ).isoformat(),
            "service_type": random.choice(SERVICE_TYPES),
            "odometer": random.randint(5000, 150000),
            "parts_cost": round(
                random.uniform(50, 5000),
                2
            ),
            "labour_cost": round(
                random.uniform(50, 2000),
                2
            ),
            "failure_code": random.choice(FAILURE_CODES),
        }

        maintenance.append(maintenance_record)

    # --------------------------------------------------------
    # Intentional data-quality issues
    # --------------------------------------------------------

    # Duplicate service ID
    maintenance[20]["service_id"] = maintenance[19]["service_id"]

    # Missing vehicle ID
    maintenance[40]["vehicle_id"] = ""

    # Negative parts cost
    maintenance[60]["parts_cost"] = -250

    return maintenance


# ============================================================
# CSV WRITING FUNCTION
# ============================================================

def write_csv(filename, data, fieldnames):

    file_path = OUTPUT_DIR / filename

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(data)

    print(f"Created: {file_path}")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("BMW ENTERPRISE BATCH ETL - DATASET GENERATOR")
    print("=" * 60)

    # --------------------------------------------------------
    # Generate datasets
    # --------------------------------------------------------

    print("\nGenerating dealer data...")
    dealers = generate_dealers()

    print("Generating vehicle master data...")
    vehicles = generate_vehicles()

    print("Generating sales data...")
    sales = generate_sales(
        vehicles,
        dealers
    )

    print("Generating maintenance data...")
    maintenance = generate_maintenance(
        vehicles,
        dealers
    )

    # --------------------------------------------------------
    # Write CSV files
    # --------------------------------------------------------

    write_csv(
        "dealer.csv",
        dealers,
        [
            "dealer_id",
            "dealer_name",
            "city",
            "region",
            "capacity",
            "rating",
        ],
    )

    write_csv(
        "vehicle_master.csv",
        vehicles,
        [
            "vehicle_id",
            "vin",
            "model",
            "model_year",
            "fuel_type",
            "region",
            "manufacturing_date",
        ],
    )

    write_csv(
        "sales.csv",
        sales,
        [
            "sale_id",
            "vehicle_id",
            "dealer_id",
            "customer_id",
            "sale_date",
            "model",
            "region",
            "price",
            "quantity",
        ],
    )

    write_csv(
        "maintenance.csv",
        maintenance,
        [
            "service_id",
            "vehicle_id",
            "dealer_id",
            "service_date",
            "service_type",
            "odometer",
            "parts_cost",
            "labour_cost",
            "failure_code",
        ],
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETED")
    print("=" * 60)

    print("\nFiles created:")
    print(f"  dealer.csv           : {len(dealers)} rows")
    print(f"  vehicle_master.csv   : {len(vehicles)} rows")
    print(f"  sales.csv            : {len(sales)} rows")
    print(f"  maintenance.csv      : {len(maintenance)} rows")

    print(f"\nOutput folder:")
    print(f"  {OUTPUT_DIR}")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()