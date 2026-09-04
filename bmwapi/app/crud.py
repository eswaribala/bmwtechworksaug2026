from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.get(Customer, customer_id)


def get_customer_by_email(db: Session, email: str) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.email == email))


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
) -> list[Customer]:
    stmt = select(Customer)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            (Customer.first_name.ilike(pattern))
            | (Customer.last_name.ilike(pattern))
            | (Customer.email.ilike(pattern))
        )
    stmt = stmt.order_by(Customer.id).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
    customer = Customer(**customer_in.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: Customer, customer_in: CustomerUpdate) -> Customer:
    update_data = customer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: Customer) -> None:
    db.delete(customer)
    db.commit()
