import json

from typing import Union
from decimal import Decimal


AmountType = Union[int, float, Decimal]


class Transaction:
    # Generate by gateway server
    id: str = None

    # Required to set from the invoice on `request` and `verify`
    amount: AmountType = None

    # Required in many gateways, usually its the invoice ID in your app.
    order_id: str = None

    # Payment Card Number fills on `verification`
    pan: str = None

    # Value given on `validation`
    validate_status: bool = False

    # Temporary data for transaction
    meta: dict = dict()

    def __init__(
        self,
        amount: AmountType = None,
        order_id: str = None,
        pan: str = None,
        meta: dict = None,
    ):
        if meta:
            self.meta = meta
        self.amount = amount
        self.order_id = order_id
        self.pan = pan

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "amount": self.amount,
            "validate_status": self.validate_status,
            "meta": self.meta,
        }

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)
