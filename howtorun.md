# How to Run the BMW Data Quality & Governance Platform

This guide provides step-by-step instructions to run the entire platform from scratch using Command Prompt (`cmd`) or PowerShell.

---

## 📋 Prerequisites

Make sure the following tools are installed:
- **Python 3.10+**: Run `python --version`
- **Node.js 18+ & npm**: Run `node -v` and `npm -v`
- **Terraform 1.6+** *(Optional - only needed to deploy AWS infrastructure)*: Run `terraform -version`
- **AWS CLI** *(Optional - only needed if connecting to real AWS account)*: Run `aws --version`

---

## 🚀 Quick Start (Running Locally with Backend & Frontend)

### Step 1: Install Python Dependencies

Open a Command Prompt or PowerShell terminal in the project root:

```cmd
pip install -r requirements.txt
```

---

### Step 2: Start the Backend API Server (Terminal 1)

In the first terminal, run:

```cmd
python -m uvicorn backend.app:app --reload --port 8000
```

> **Note**: The backend starts at **`http://localhost:8000`**.
> You can verify it is healthy by visiting: [http://localhost:8000/health](http://localhost:8000/health)

---

### Step 3: Start the Frontend UI (Terminal 2)

Open a **second** terminal window and navigate to `frontend`:

```cmd
cd frontend
npm install
npm run dev
```

> **Note**: The frontend starts at **`http://localhost:5173`**.

---

### Step 4: Validate CSV Files via UI

1. Open your browser and navigate to **`http://localhost:5173`**.
2. Go to the **Validate / Upload** tab.
3. Drag & drop or browse to select one of the sample CSV datasets:
   - `data/sample/bmw_vehicle_master.csv`
   - `data/sample/bmw_telemetry.csv`
4. The system will automatically:
   - Upload the file to S3 `raw/<dataset>/` (or fallback to local if AWS credentials are not configured).
   - Execute null checks, duplicate checks, VIN regex, date parsing, and referential integrity checks against `vehicle_master`.
   - Segregate records into **Curated** (valid) and **Quarantine** (rejected).
   - Display the real-time **Quality Score (0–100)**, status gauge, check breakdown, and S3 paths on screen.

---

## ☁️ Deploying AWS Infrastructure (Terraform)

If you want to deploy the S3 bucket, IAM role, CloudWatch monitoring, Glue Catalog, and Athena workgroup to your AWS account:

### 1. Configure AWS Credentials
Make sure your AWS credentials are set:
```cmd
aws configure
```

### 2. Initialize and Apply Terraform
Navigate to the `terraform` folder:
```cmd
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
```

This provisions:
- **S3 Data Lake Bucket**:
  - `raw/telemetry/`
  - `raw/vehicle_master/`
  - `curated/`
  - `quarantine/`
  - `reports/` (with `reports/athena-results/`)
  - `logs/`
- **IAM Role & Policies**: Granular permissions for S3, CloudWatch, Glue, and Athena.
- **CloudWatch**: Log group (`/bmw/data-quality`), metrics (`QualityScore`, `RejectedRecords`), and dashboard.
- **AWS Glue**: Database `bmw_data_quality` and catalog tables.
- **Amazon Athena**: Workgroup `bmw-data-quality` with sample SQL queries.

---

## 💻 Alternative: Running via CLI (Without UI)

You can also run the quality engine directly from the command line:

### Validate Vehicle Master:
```cmd
python src/main.py --dataset vehicle_master --input data/sample/bmw_vehicle_master.csv --local
```

### Validate Telemetry:
```cmd
python src/main.py --dataset telemetry --input data/sample/bmw_telemetry.csv --local
```

### Inspect Output Results:
Check the `output/` directory for generated files:
- `output/curated/` — Clean, validated CSV files
- `output/quarantine/` — Rejected records with error reason tags
- `output/reports/` — Detailed JSON and TXT quality summary reports

---

## 🧪 Running Automated Tests

To run the unit and integration test suite:

```cmd
pytest
```
