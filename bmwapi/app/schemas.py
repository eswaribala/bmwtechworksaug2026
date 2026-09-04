from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100, examples=["John"])
    last_name: str = Field(min_length=1, max_length=100, examples=["Doe"])
    email: EmailStr = Field(examples=["john.doe@example.com"])
    phone: str | None = Field(default=None, max_length=20, examples=["+1-555-123-4567"])
    address: str | None = Field(default=None, max_length=255, examples=["123 Main St, Springfield"])
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
