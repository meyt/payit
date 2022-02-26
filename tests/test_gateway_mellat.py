import mock
import pytest

from payit import Transaction, TransactionError, GatewayNetworkError
from payit.gateways import MellatGateway
from tests.mockup.mellat_gateway import get_side_effect


config = {
    "terminal_id": "1234",
    "username": "demo",
    "password": "demo",
    "callback_url": "http://localhost/callback",
    "proxies": "socks5://127.0.0.1:9050",
}


def domock(sideeffect):
    return mock.patch("payit.gateways.mellat.Client", side_effect=sideeffect)


def test_gateway():
    gateway = MellatGateway(config=config)
    with domock(get_side_effect(returned_token="0,4444")):
        transaction = gateway.request_transaction(
            Transaction(amount=1000, order_id=1)
        )
        gateway.get_redirection(transaction)

        valid_transaction = gateway.validate_transaction(
            {"RefId": "4444", "ResCode": "0"}
        )
        assert valid_transaction.validate_status

        invalid_transaction = gateway.validate_transaction(
            {"RefId": "4444", "ResCode": "300"}
        )
        assert not invalid_transaction.validate_status

    # success transaction
    with domock(get_side_effect(verify_result=0)):
        gateway.verify_transaction(
            transaction, dict(SaleOrderId="44441", SaleReferenceId="44442")
        )

    # failed transaction
    with domock(get_side_effect(verify_result=100)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(
                transaction, dict(SaleOrderId="44441", SaleReferenceId="44442")
            )

    # settle fail
    with domock(get_side_effect(settle_result=100)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(
                transaction, dict(SaleOrderId="44441", SaleReferenceId="44442")
            )

    # network error
    with domock(get_side_effect(raise_zeep_error=True)):
        with pytest.raises(GatewayNetworkError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

        with pytest.raises(GatewayNetworkError):
            gateway.verify_transaction(
                transaction, dict(SaleOrderId="44441", SaleReferenceId="44442")
            )

    # invalid token
    with domock(get_side_effect(returned_token=100)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # no token
    with domock(get_side_effect(returned_token=None)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # zeep fault
    with domock(get_side_effect(raise_zeep_fault=True)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))
