from datetime import date
from typing import Any

from pydantic import BaseModel, Field


# --------------------------------------------------
# API Request
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Natural language BMW analytics question",
    )


# --------------------------------------------------
# API Response
# --------------------------------------------------

class AnalysisResponse(BaseModel):
    question: str
    sql: str | None = None
    data: list[dict[str, Any]] = Field(default_factory=list)
    answer: str


# --------------------------------------------------
# Vehicle Sales
# --------------------------------------------------

class VehicleSale(BaseModel):
    vehicle_id: int
    model: str
    city: str
    sale_date: date
    sales_amount: float
    quantity: int


# --------------------------------------------------
# Warranty
# --------------------------------------------------

class WarrantyRecord(BaseModel):
    vehicle_id: int
    model: str
    city: str
    warranty_date: date
    fault_type: str
    warranty_cost: float


# --------------------------------------------------
# Fault Summary
# --------------------------------------------------

class FaultSummary(BaseModel):
    fault_type: str
    severity: str
    fault_count: int


# --------------------------------------------------
# Battery Status
# --------------------------------------------------

class BatteryStatus(BaseModel):
    vehicle_id: int
    model: str
    city: str
    battery_date: date
    battery_percentage: float
    battery_status: str