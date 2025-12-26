# backend/payoneer.py
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class Payout(BaseModel):
    date: str
    amount: float
    currency: str = "USD"
    status: str = "Completed"

MOCK_PAYOUTS = [
    Payout(date="2024-12-30", amount=284.22),
    Payout(date="2025-01-30", amount=311.50),
    Payout(date="2025-02-29", amount=296.88),
    Payout(date="2025-03-30", amount=333.99),
]

@router.get("/api/v1/payouts")
def get_payouts():
    return {"payouts": MOCK_PAYOUTS}
