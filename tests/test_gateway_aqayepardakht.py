import mock
import pytest

from payit import (
    Transaction,
    TransactionError,
    GatewayNetworkError,
    TransactionAlreadyPaidError,
)
from payit.gateways import AqayepardakhtGateway
from tests.mockup.aqayerpardakht_gateway import get_side_effect


config = {
    "pin": "aqayepardakht",
    "callback_url": "http://localhost/callback",
}


def domock(sideeffect):
    return mock.patch(
        "payit.gateways.aqayepardakht.request", side_effect=sideeffect
    )


def test_gateway():
    gateway = AqayepardakhtGateway(config=config)
    with domock(get_side_effect(returned_text="11-22-33")):
        transaction = gateway.request_transaction(
            Transaction(amount=1000, order_id=1)
        )
        gateway.get_redirection(transaction)

        # with optional fields
        transaction = gateway.request_transaction(
            Transaction(amount=1000, order_id=1, meta=dict(invoice_id="112"))
        )
        gateway.get_redirection(transaction)

        valid_transaction = gateway.validate_transaction(
            {"transid": "RETURNED_TOKEN", "status": "1"}
        )
        assert valid_transaction.validate_status

        invalid_transaction = gateway.validate_transaction({})
        assert not invalid_transaction.validate_status

    # success verification
    with domock(get_side_effect(returned_text="1")):
        gateway.verify_transaction(transaction, dict())

    # failed verification
    with domock(get_side_effect(returned_text="0")):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # already paid
    with domock(get_side_effect(returned_text="2")):
        with pytest.raises(TransactionAlreadyPaidError):
            gateway.verify_transaction(transaction, dict())

    # invalid transaction
    with domock(get_side_effect(http_status_code=402)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000))

        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # network error
    with domock(get_side_effect(raise_url_error=True)):
        with pytest.raises(GatewayNetworkError):
            gateway.verify_transaction(transaction, dict())

        with pytest.raises(GatewayNetworkError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))
