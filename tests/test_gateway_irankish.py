import mock
import pytest

from payit import (
    Transaction,
    TransactionError,
    GatewayNetworkError,
    TransactionAlreadyPaidError,
)
from payit.gateways import IrankishGateway
from tests.mockup.irankish_gateway import get_side_effect


config = {
    "merchant": "C0C1",
    "sha1key": "212320992352934514917221765200141041845518824222260",
    "callback_url": "http://localhost/callback",
    "proxies": "socks5://127.0.0.1:9050",
}


def domock(sideeffect):
    return mock.patch("payit.gateways.irankish.Client", side_effect=sideeffect)


def test_gateway():
    gateway = IrankishGateway(config=config)
    with domock(get_side_effect()):
        transaction = gateway.request_transaction(
            Transaction(amount=1000, order_id=1)
        )
        gateway.get_redirection(transaction).to_dict()

        valid_transaction = gateway.validate_transaction(
            {"token": "RETURNED_TOKEN", "resultCode": "100"}
        )
        assert valid_transaction.validate_status

        invalid_transaction = gateway.validate_transaction(
            {"token": "RETURNED_TOKEN", "resultCode": "300"}
        )
        assert not invalid_transaction.validate_status

    # success verification
    with domock(get_side_effect(verify_result=1000)):
        gateway.verify_transaction(transaction, dict())

    # failed transaction
    with domock(get_side_effect()):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # unknown error
    with domock(get_side_effect(verify_result=-900)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # network error
    with domock(get_side_effect(raise_zeep_error=True)):
        with pytest.raises(GatewayNetworkError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

        with pytest.raises(GatewayNetworkError):
            gateway.verify_transaction(transaction, dict())

    # already paid
    with domock(get_side_effect(verify_result=-90)):
        with pytest.raises(TransactionAlreadyPaidError):
            gateway.verify_transaction(transaction, dict())

    # no token
    with domock(get_side_effect(returned_token=None)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # zeep fault
    with domock(get_side_effect(raise_zeep_fault=True)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))
