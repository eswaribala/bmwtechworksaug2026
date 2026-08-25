from contextlib import asynccontextmanager

from fastapi import FastAPI

from vehiclemodule.configurations.postgres_conn import base, engine

# Import model before create_all so SQLAlchemy registers it
from vehiclemodule.models.vehicle import Vehicle

from vehiclemodule.controllers.vehicle_controller import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Vehicle Management API",
    description="API for managing vehicles",
    version="1.0",
    lifespan=lifespan
)


app.include_router(router)