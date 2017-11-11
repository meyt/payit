

class Transaction:
    """
    Attributes:
        id                  Generate by gateway server 
        order_id            Required, and must unique per transaction
        amount              Required to set from your invoice on `request` and `verify`
        validate_status     Value given on `validation`
        meta                Temporary data for transaction
    """
    id = None
    order_id = None
    amount = None
    validate_status = False
    meta = dict()

    def __init__(self, amount=None, order_id=None, meta: dict=None):
        if meta:
            self.meta = meta
        self.amount = amount
        self.order_id = order_id

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': self.amount,
            'validate_status': self.validate_status,
            'meta': self.meta
        }
