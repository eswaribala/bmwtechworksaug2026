# BMW Natural Language Data Analyst

## Overview

The **BMW Natural Language Data Analyst** allows business users to ask BMW analytics questions using natural language instead of manually writing SQL queries.

The application converts a natural-language question into a secure, read-only SQL query, validates the generated SQL, executes the approved query through MCP against Snowflake, and generates a business-friendly natural-language explanation of the results.

The application uses:

- Python
- Ollama with the local model `llama3.2:1b`
- MCP (Model Context Protocol)
- Snowflake
- FastAPI
- Streamlit
- Terraform
- Pytest
- GitHub Actions

---

## Architecture

The BMW Natural Language Analyst follows a linear processing architecture:

```text
User
  |
  v
Streamlit UI / FastAPI
  |
  v
BMW Analyst Agent
  |
  v
Intent Router
  |
  v
Ollama - Llama 3.2 1B
  |
  v
SQL Generation
  |
  v
SQL Security Validator
  |
  v
MCP Client
  |
  v
MCP Server
  |
  v
Approved Query Tool
  |
  v
Snowflake
  |
  v
Query Result
  |
  v
Ollama - Llama 3.2 1B
  |
  v
Narrative Response
  |
  v
Streamlit UI / API Response
  |
  v
User
```

---

## Application Flow

A typical request follows this flow:

```text
Natural Language Question
          |
          v
      Intent Router
          |
          v
   Llama 3.2 1B
          |
          v
    SQL Generation
          |
          v
    SQL Validation
          |
          v
      MCP Client
          |
          v
      MCP Server
          |
          v
execute_approved_query()
          |
          v
       Snowflake
          |
          v
     Query Result
          |
          v
   Llama 3.2 1B
          |
          v
 Narrative Explanation
          |
          v
         User
```

---

## Technologies

| Technology | Purpose |
|---|---|
| Python | Application development |
| Ollama | Local LLM runtime |
| Llama 3.2 1B | SQL generation and narrative response generation |
| MCP | Tool-based communication between the agent and data layer |
| Snowflake | BMW analytical data warehouse |
| FastAPI | Backend REST API |
| Streamlit | User interface |
| Terraform | Snowflake infrastructure provisioning |
| Pytest | Automated testing |
| GitHub Actions | CI automation |

---

## BMW Analyst Agent

The `BMWAnalystAgent` coordinates the application workflow.

Responsibilities include:

- Intent detection
- SQL generation
- SQL validation
- MCP execution
- Result processing
- Narrative response generation

The agent does not directly execute arbitrary SQL against Snowflake.

All generated SQL must pass the SQL security validation layer before execution.

---

## Intent Router

The Intent Router identifies the category of the user's BMW analytics question.

Supported analytical categories include:

```text
vehicle_sales
warranty_cost
fault_summary
battery_status
```

For unsupported questions, the application returns a user-friendly response instead of exposing internal SQL validation errors.

Example:

```text
I can only answer questions related to BMW analytical
data, such as vehicle sales, warranty costs, faults,
and battery status.
```

Internal validation details remain in the application logs and are not exposed to business users.

---

## Ollama

The application uses Ollama with the local model:

```text
llama3.2:1b
```

Ollama is used for:

- SQL generation
- Narrative response generation

Default configuration:

```text
http://127.0.0.1:11434
```

Pull the model:

```powershell
ollama pull llama3.2:1b
```

Verify the installed model:

```powershell
ollama list
```

---

# MCP Tools

The MCP server provides the following tools:

```text
vehicle_sales
warranty_cost
fault_summary
battery_status
execute_approved_query
```

The dynamically generated analytical SQL is executed through:

```text
execute_approved_query()
```

The MCP client starts the MCP server as a subprocess using the current Python interpreter.

The MCP client maintains a persistent MCP session to reduce the overhead of creating a new MCP process and session for every request.

Always activate the project virtual environment before starting the API or running tests:

```powershell
.\bmwvenv\Scripts\Activate.ps1
```

---

# Snowflake

## Database

```text
BMW_ANALYTICS
```

## Schema

```text
BMW_DATA
```

## Warehouse

```text
BMW_WH
```

## Read-only Role

```text
BMW_ANALYST_READONLY
```

## Approved Tables

```text
BMW_VEHICLE_SALES
BMW_WARRANTY
BMW_FAULTS
BMW_BATTERY
```

The application is designed to access only the approved BMW analytical tables.

---

# Security

The application implements multiple layers of security.

## SQL Security

All generated SQL passes through SQL validation before execution.

The validator enforces:

- SELECT-only SQL
- Single-statement validation
- Approved database validation
- Approved schema validation
- Approved table validation
- Approved column validation
- Blocked SQL commands
- Maximum 1000 returned rows
- 30-second query timeout
- Maximum question length of 1000 characters
- Application audit logging

Blocked operations include:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
MERGE
GRANT
REVOKE
```

The SQL validator remains strict even when a user submits an unrelated or unsupported question.

Unsupported questions are handled at the application/agent level with a friendly response.

## Snowflake Security

The application uses:

```text
BMW_ANALYST_READONLY
```

for analytical access.

The application does not require write access to the BMW analytics tables.

---

# Configuration

Create a `.env` file in the project root:

```env
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_AUTHENTICATOR=snowflake
SNOWFLAKE_ROLE=BMW_ANALYST_READONLY
SNOWFLAKE_WAREHOUSE=BMW_WH
SNOWFLAKE_DATABASE=BMW_ANALYTICS
SNOWFLAKE_SCHEMA=BMW_DATA

OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:1b

API_HOST=127.0.0.1
API_PORT=8000

STREAMLIT_HOST=127.0.0.1
STREAMLIT_PORT=8501

MCP_SERVER_NAME=BMW Natural Language Analyst
APP_NAME=BMW Natural Language Data Analyst
LOG_LEVEL=INFO
```

Never commit `.env` or credentials to Git.

The `.env` file should be included in `.gitignore`.

---

# Installation

From the project root:

```powershell
cd C:\bmw-natural-language-analyst
```

Activate the virtual environment:

```powershell
.\bmwvenv\Scripts\Activate.ps1
```

Install the project:

```powershell
python -m pip install -e .
```

For development and testing:

```powershell
python -m pip install -e ".[dev]"
```

---

# Run FastAPI

From the project root:

```powershell
cd C:\bmw-natural-language-analyst
```

Activate the environment:

```powershell
.\bmwvenv\Scripts\Activate.ps1
```

Set the Python path:

```powershell
$env:PYTHONPATH="$PWD\src;$PWD"
```

Start FastAPI:

```powershell
python -m uvicorn bmw_analyst.api.main:app --host 127.0.0.1 --port 8000 --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Health Check

Endpoint:

```text
GET /health
```

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "bmw-natural-language-analyst"
}
```

---

# Readiness Check

The readiness endpoint verifies connectivity to Snowflake.

```text
GET /ready
```

The endpoint executes a Snowflake connectivity check.

---

# Run Streamlit

Open another PowerShell terminal:

```powershell
cd C:\bmw-natural-language-analyst
```

Activate the environment:

```powershell
.\bmwvenv\Scripts\Activate.ps1
```

Set the Python path:

```powershell
$env:PYTHONPATH="$PWD\src;$PWD"
```

Start Streamlit:

```powershell
python -m streamlit run ui\streamlit_app.py
```

The Streamlit application normally runs at:

```text
http://localhost:8501
```

---

# API Example

## Request

```http
POST /ask
```

Request body:

```json
{
  "question": "Which BMW model had the highest warranty cost in Chennai?"
}
```

## Example Response

```json
{
  "question": "Which BMW model had the highest warranty cost in Chennai?",
  "intent": "warranty_cost",
  "sql": "SELECT ...",
  "data": [
    {
      "MODEL": "BMW i5",
      "TOTAL_WARRANTY_COST": 1136000
    }
  ],
  "answer": "The BMW i5 had the highest warranty cost in Chennai, with a total warranty cost of INR 11,36,000."
}
```

The exact result depends on the data available in Snowflake.

---

# Unsupported Questions

The application is designed to handle unrelated questions without exposing internal errors.

For example:

```text
What is the capital of France?
```

The application should return a friendly response such as:

```text
I can only answer questions related to BMW analytical
data, such as vehicle sales, warranty costs, faults,
and battery status.
```

The user should not receive internal messages such as:

```text
Generated SQL failed security validation.
```

Internal technical details are logged for troubleshooting.

---

# Example BMW Questions

```text
Which BMW model had the highest warranty cost in Chennai?

Which city had the highest vehicle sales?

What is the most common fault type?

Which BMW models have battery percentage below 30%?

Compare warranty costs between BMW X5 and BMW iX.

Which BMW model has the highest number of reported faults?

What are the battery statuses of BMW vehicles in Chennai?
```

---

# Testing

Run the complete test suite:

```powershell
python -m pytest -q
```

Run tests excluding integration tests:

```powershell
python -m pytest -q -m "not integration"
```

Run SQL security tests:

```powershell
python -m pytest tests\test_sql_validator.py -v
```

Run MCP client tests:

```powershell
python -m pytest tests\test_mcp_client.py -v
```

Run MCP tool tests:

```powershell
python -m pytest tests\test_mcp_tools.py -v
```

Run API tests:

```powershell
python -m pytest tests\test_api.py -v
```

Run Snowflake integration tests:

```powershell
python -m pytest tests\test_snowflake.py -v
```

Snowflake integration tests require valid Snowflake credentials and connectivity.

---

# Test Coverage

The test suite covers:

- Snowflake connectivity
- MCP tools
- MCP client
- SQL validation
- Query limits
- Intent routing
- Agent behavior
- API behavior
- Security behavior
- Unsupported questions
- Query execution

---

# Logging

Application logs are stored in:

```text
logs\bmw_analyst.log
```

The application records events such as:

- API requests
- Request IDs
- Intent detection
- SQL generation
- SQL validation
- MCP execution
- Snowflake execution
- Query row counts
- Narrative generation
- Errors

Sensitive credentials must never be written to application logs.

For rejected requests, technical details are logged internally while the user receives a safe, business-friendly response.

---

# Terraform

Terraform is used for Snowflake infrastructure provisioning.

Terraform manages infrastructure such as:

- Database
- Schema
- Warehouse
- Tables
- Roles
- Grants
- Security configuration

Terraform directory:

```text
terraform/
└── snowflake/
    ├── database.tf
    ├── schema.tf
    ├── tables.tf
    ├── warehouse.tf
    ├── security.tf
    ├── provider.tf
    └── variables.tf
```

Initialize Terraform:

```powershell
terraform init
```

Validate the configuration:

```powershell
terraform validate
```

Create a plan:

```powershell
terraform plan
```

Apply the infrastructure when required:

```powershell
terraform apply
```

When the infrastructure is already synchronized, Terraform can report:

```text
No changes. Your infrastructure matches the configuration.
```

---

# Project Structure

```text
bmw-natural-language-analyst/
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── src/
│   └── bmw_analyst/
│       │
│       ├── agent/
│       │   ├── agent.py
│       │   ├── router.py
│       │   ├── sql_generator.py
│       │   └── prompts.py
│       │
│       ├── api/
│       │   ├── main.py
│       │   └── metrics.py
│       │
│       ├── mcp_client/
│       │   ├── client.py
│       │   └── models.py
│       │
│       ├── mcp_server/
│       │   ├── server.py
│       │   ├── tools.py
│       │   └── schemas.py
│       │
│       ├── models/
│       │   └── schemas.py
│       │
│       ├── security/
│       │   ├── sql_validator.py
│       │   ├── permissions.py
│       │   └── logging_config.py
│       │
│       └── snowflake/
│           ├── connection.py
│           ├── executor.py
│           └── queries.py
│
├── tests/
│   ├── test_api.py
│   ├── test_agent.py
│   ├── test_mcp_client.py
│   ├── test_mcp_tools.py
│   ├── test_router.py
│   ├── test_sql_validator.py
│   ├── test_query_limits.py
│   └── test_snowflake.py
│
├── ui/
│   └── streamlit_app.py
│
├── terraform/
│   └── snowflake/
│
├── data/
│   └── sample/
│
├── logs/
│
├── docs/
│   ├── source/
│   └── build/
│
├── .github/
│   └── workflows/
│
├── .env
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── run.py
└── README.md
```

---

# End-to-End Example

Example question:

```text
Which BMW model had the highest warranty cost in Chennai?
```

The request follows the complete pipeline:

```text
User
  |
  v
Streamlit
  |
  v
FastAPI
  |
  v
BMW Analyst Agent
  |
  v
Intent Router
  |
  v
warranty_cost
  |
  v
Ollama - Llama 3.2 1B
  |
  v
SQL Generation
  |
  v
SQL Security Validator
  |
  v
MCP Client
  |
  v
MCP Server
  |
  v
execute_approved_query()
  |
  v
Snowflake
  |
  v
Query Result
  |
  v
Ollama - Llama 3.2 1B
  |
  v
Narrative Explanation
  |
  v
Streamlit
  |
  v
User
```

For the acceptance question, the verified analytical result is:

```text
BMW i5
Total Warranty Cost: INR 11,36,000
```

---

# CI/CD

GitHub Actions is used for automated testing.

Workflow location:

```text
.github/
└── workflows/
    └── ci.yml
```

The CI pipeline performs:

```text
Git Push / Pull Request
        |
        v
GitHub Actions
        |
        v
Python Setup
        |
        v
Install Dependencies
        |
        v
Run Tests
        |
        v
PASS / FAIL
```

---

# Current Status

## Implemented

- Project structure
- Snowflake connectivity
- Persistent Snowflake connection
- Terraform infrastructure
- SQL security validation
- MCP server
- Persistent MCP client
- MCP tools
- Intent routing
- Local Ollama integration
- Llama 3.2 1B
- SQL generation
- Query limits
- FastAPI API
- Streamlit integration
- Audit logging
- Automated tests
- GitHub Actions CI
- Sphinx documentation

## Security Controls

```text
SELECT-only SQL
Single statement
Approved database
Approved schema
Approved tables
Approved columns
Read-only Snowflake role
1000-row limit
30-second timeout
1000-character question limit
Audit logging
```

---

# Performance

The application uses persistent connections where appropriate.

The MCP client maintains a persistent MCP session.

The Snowflake connection is reused between queries.

This reduces the overhead associated with creating a new MCP session and Snowflake connection for every request.

---

# Troubleshooting

## MCP Connection Error

If you see:

```text
ModuleNotFoundError
```

or:

```text
McpError: Connection closed
```

activate the project virtual environment:

```powershell
.\bmwvenv\Scripts\Activate.ps1
```

Set the Python path:

```powershell
$env:PYTHONPATH="$PWD\src;$PWD"
```

Run the MCP client tests:

```powershell
python -m pytest tests\test_mcp_client.py -q
```

The MCP server is started automatically by the MCP client.

---

## Ollama Model Not Found

Check installed models:

```powershell
ollama list
```

Pull the required model:

```powershell
ollama pull llama3.2:1b
```

Verify the environment configuration:

```text
OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

---

## Snowflake Connection Error

Verify:

```text
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_PASSWORD
SNOWFLAKE_AUTHENTICATOR
SNOWFLAKE_ROLE
SNOWFLAKE_WAREHOUSE
SNOWFLAKE_DATABASE
SNOWFLAKE_SCHEMA
```

The application should use:

```text
BMW_ANALYST_READONLY
```

for normal analytical operations.

---

# Documentation

Project documentation is maintained using Sphinx.

Build the documentation:

```powershell
python -m sphinx -b html docs\source docs\build\html
```

Open the documentation:

```powershell
start docs\build\html\index.html
```

Documentation includes:

```text
Architecture
Installation
Configuration
API
MCP
Snowflake
Security
Testing
Terraform
Project Structure
```

---

# Design Principles

The project follows these principles:

1. Natural-language-first analytics
2. Local LLM processing using Ollama
3. Read-only analytical access
4. SQL validation before execution
5. MCP-based tool communication
6. Snowflake-based analytical storage
7. Separation of application layers
8. Automated testing
9. Environment-based configuration
10. No credentials stored in source code
11. Friendly user-facing error handling
12. Internal technical errors remain in application logs
13. Persistent MCP and Snowflake connections where appropriate

---

# License

Internal BMW TechWorks training/project use.
