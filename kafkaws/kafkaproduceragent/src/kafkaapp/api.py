import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from confluent_kafka import KafkaException, Producer
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from kafkaapp.schemas import SalesRequest, SalesEvent, AgentRequest
from starlette.concurrency import run_in_threadpool

# This module loads the project's .env file.
from kafkaapp.kafkaagent import run_agent
from kafkaapp.schemas import (
    AgentRequest,
    SalesRequest,
    SalesEvent,
)
PROJECT_ROOT=Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)

TOPIC = os.getenv("KAFKA_TOPIC")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.producer = Producer(
        {
            "bootstrap.servers": os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS"
            ),
            "broker.address.family": "v4",
            "client.id": "bmw-agent-producer",
            "acks": "all",
            "enable.idempotence": True,
            "delivery.timeout.ms": 10000,
        }
    )

    # Simple lab implementation: one publish-and-flush at a time.
    app.state.publish_lock = Lock()

    try:
        yield
    finally:
        remaining = await run_in_threadpool(
            app.state.producer.flush,
            12,
        )

        if remaining:
            logger.warning(
                "Shutdown with %s unconfirmed messages",
                remaining,
            )


app = FastAPI(
    title="BMW Agent Kafka Publisher",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {
        "application": "BMW Agent Kafka Publisher",
        "docs": "/docs",
    }


@app.post("/publish_sales_data", status_code=201)
def publish_sales_data(
    payload: SalesRequest,
    request: Request,
):
    producer = request.app.state.producer

    event = SalesEvent(
        **payload.model_dump(),
        timestamp=datetime.now(timezone.utc),
    )

    delivery = {}

    def delivery_report(error, message):
        if error is not None:
            delivery["error"] = str(error)
        else:
            delivery["partition"] = message.partition()
            delivery["offset"] = message.offset()

    with request.app.state.publish_lock:
        try:
            producer.produce(
                topic=TOPIC,
                key=str(event.product_id).encode("utf-8"),
                value=event.model_dump_json().encode("utf-8"),
                on_delivery=delivery_report,
            )

            # Executes delivery callbacks while waiting.
            producer.flush(12)

        except BufferError as error:
            raise HTTPException(
                status_code=503,
                detail="Kafka producer queue is full.",
            ) from error

        except KafkaException as error:
            raise HTTPException(
                status_code=503,
                detail=f"Kafka publishing error: {error}",
            ) from error

    if "error" in delivery:
        raise HTTPException(
            status_code=503,
            detail=f"Kafka delivery failed: {delivery['error']}",
        )

    if "offset" not in delivery:
        raise HTTPException(
            status_code=504,
            detail=(
                "Kafka acknowledgement timed out. Delivery is unknown; "
                "retrying may duplicate the event."
            ),
        )

    return {
        "status": "delivered",
        "topic": TOPIC,
        "partition": delivery["partition"],
        "offset": delivery["offset"],
        "event": event.model_dump(mode="json"),
    }


@app.post("/agent/publish")
def agent_publish(payload: AgentRequest):
    try:
        return run_agent(payload.message)
    except Exception as error:
        logger.exception("Agent request failed")

        raise HTTPException(
            status_code=502,
            detail=(
                "Agent execution failed. Check the server terminal "
                "for AWS credentials, model access, or configuration errors."
            ),
        ) from error