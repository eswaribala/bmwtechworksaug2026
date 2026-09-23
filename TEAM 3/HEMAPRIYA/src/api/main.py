from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.recommendation.recommendation_engine import recommend_inventory


# ------------------------------------------------------------
# PROJECT PATH
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = PROJECT_ROOT / "data" / "dealer_inventory_features.csv"


# ------------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ------------------------------------------------------------

app = FastAPI(
    title="BMW Dealer Inventory Recommendation API",
    description="API for recommending BMW inventory by dealer and model",
    version="1.0.0",
)


# ------------------------------------------------------------
# CORS CONFIGURATION
# ------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# REQUEST MODEL
# ------------------------------------------------------------

class RecommendationRequest(BaseModel):
    dealer_id: str
    model: str


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ------------------------------------------------------------
# GET AVAILABLE DEALERS AND MODELS
# ------------------------------------------------------------

@app.get("/options")
def get_options():

    try:

        df = pd.read_csv(DATA_FILE)

        dealers = sorted(
            df["dealer_id"]
            .dropna()
            .unique()
            .tolist()
        )

        models = sorted(
            df["model"]
            .dropna()
            .unique()
            .tolist()
        )

        return {
            "dealers": dealers,
            "models": models,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load dealer/model options: {str(e)}",
        )


@app.get("/history")
def get_history(dealer_id: str, model: str):

    try:
        df = pd.read_csv(DATA_FILE)
        selected = df[
            (df["dealer_id"] == dealer_id)
            & (df["model"] == model)
        ].sort_values("month").tail(12)

        if selected.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No history found for dealer {dealer_id} and model {model}.",
            )

        return {
            "months": selected["month"].tolist(),
            "actual_sales": selected["sales"].astype(float).tolist(),
            "predicted_demand": selected["next_month_sales"].astype(float).tolist(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load sales history: {str(e)}",
        )


# ------------------------------------------------------------
# INVENTORY RECOMMENDATION
# ------------------------------------------------------------

@app.post("/recommend")
def get_recommendation(request: RecommendationRequest):

    try:

        result = recommend_inventory(
            dealer_id=request.dealer_id,
            model_name=request.model,
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )