import mock
import pytest

from payit import Transaction, TransactionError, GatewayNetworkError
from payit.gateways import PayIrGateway
from tests.mockup.payir_gateway import get_side_effect


config = {
    "pin": "8523528",
    "callback_url": "http://localhost/callback",
}


def domock(sideeffect):
    return mock.patch("payit.gateways.payir.request", side_effect=sideeffect)


def test_pay_ir():
    gateway = PayIrGateway(config=config)
    with domock(get_side_effect()):
        transaction = gateway.request_transaction(
            Transaction(amount=1000, order_id=1)
        )
        gateway.get_redirection(transaction)

        # optional meta fields
        gateway.request_transaction(
            Transaction(amount=1000, meta=dict(validCardNumber="123"))
        )

        valid_transaction = gateway.validate_transaction(
            {"token": "RETURNED_TOKEN", "status": "1"}
        )
        assert valid_transaction.validate_status

        invalid_transaction = gateway.validate_transaction(
            {"token": "RETURNED_TOKEN", "status": "300"}
        )
        assert not invalid_transaction.validate_status

    # success verification
    with domock(get_side_effect(returned_status=1, returned_amount=1000)):
        gateway.verify_transaction(transaction, dict())

    # failed verification
    with domock(get_side_effect(returned_status=300, returned_amount=400)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # verification mismatch amount
    with domock(get_side_effect(returned_status=1, returned_amount=600)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # invalid transaction
    with domock(get_side_effect(http_status_code=402)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    with domock(get_side_effect(http_status_code=422, invalid_json=True)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # invalid transaction id
    with domock(get_side_effect(http_status_code=422)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # verification network error
    with domock(get_side_effect(raise_url_error=True)):
        with pytest.raises(GatewayNetworkError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

        with pytest.raises(GatewayNetworkError):
            gateway.verify_transaction(transaction, dict())
