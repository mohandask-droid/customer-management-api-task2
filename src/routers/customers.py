from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Customer
from ..schemas import CustomerCreate, CustomerUpdate, CustomerOut
from ..security import verify_api_key

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    dependencies=[Depends(verify_api_key)],
)


def get_or_404(db: Session, customer_id: int) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found")
    return customer


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Customer).where(Customer.email == data.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists")
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=list[CustomerOut])
def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Customer).order_by(Customer.id).offset((page - 1) * per_page).limit(per_page)
    return db.scalars(stmt).all()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = get_or_404(db, customer_id)
    changes = data.model_dump(exclude_unset=True)
    new_email = changes.get("email")
    if new_email and new_email != customer.email:
        if db.scalar(select(Customer).where(Customer.email == new_email)):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists")
    for key, value in changes.items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = get_or_404(db, customer_id)
    db.delete(customer)
    db.commit()