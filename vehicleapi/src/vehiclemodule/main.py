#call controller and create models
from vehiclemodule.configurations.postgres_conn import base, engine

from fastapi import FastAPI


app=FastAPI(title="Vehicle Management API", 
            description="API for managing vehicles", 
            version="1.0")

from vehiclemodule.models.vehicle import Vehicle

#generate the tables in the database
base.metadata.create_all(bind=engine)


from vehiclemodule.controllers.vehicle_controller import router
app.include_router(router)