from payit import Transaction


def test_transaction():
    transaction = Transaction(
        amount=1000,
        order_id=1,
        meta=dict(card_number="xyz"),
    )
    transaction_dict = transaction.to_dict()
    assert transaction_dict["amount"] == transaction.amount
