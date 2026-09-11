
from pydantic import BaseModel, ConfigDict, Field,Co
class SalesRequest(BaseModel):
    model_config=ConfigDict(
     from_attributes=True,
     extra="forbid",
     allow_inf_nan=False
    )

    product_id: int=Field(..., description="The ID of the product",gt=0)
    quantity: int=Field(..., description="The quantity of the product",gt=0)
    price: float=Field(..., description="The price of the product",gt=0)
    total: float=Field(..., description="The total price for the quantity of the product",gt=0)
    region: str=Field(..., description="The region where the sale occurred"
                      , example="North America", pattern="^[A-Za-z ]+$"
                      )