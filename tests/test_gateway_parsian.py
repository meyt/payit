import mock
import pytest

from payit import (
    Transaction,
    TransactionError,
    GatewayNetworkError,
    TransactionAlreadyPaidError,
)
from payit.gateways import ParsianGateway
from tests.mockup.parsian_gateway import get_side_effect


config = {
    "pin": "1234",
    "callback_url": "http://localhost/callback",
    "proxies": "socks5://127.0.0.1:9050",
}


def domock(sideeffect):
    return mock.patch("payit.gateways.parsian.Client", side_effect=sideeffect)


def test_gateway():
    gateway = ParsianGateway(config=config)
    with domock(get_side_effect(returned_token="4444")):
        transaction = gateway.request_transaction(
            Transaction(amount=1000, order_id=1)
        )
        gateway.get_redirection(transaction)

        valid_transaction = gateway.validate_transaction(
            {"Token": "4444", "status": "0"}
        )
        assert valid_transaction.validate_status

        invalid_transaction = gateway.validate_transaction(
            {"Token": "4444", "status": "300"}
        )
        assert not invalid_transaction.validate_status

    # success verification
    with domock(get_side_effect(returned_status=0)):
        gateway.verify_transaction(
            transaction, dict(OrderId="44441", Token="44442")
        )

    # failed verification
    with domock(get_side_effect(returned_status=-100)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(
                transaction, dict(OrderId="44441", Token="44442")
            )

    # already verified
    with domock(get_side_effect(returned_status=-1533)):
        with pytest.raises(TransactionAlreadyPaidError):
            gateway.verify_transaction(
                transaction, dict(OrderId="44441", Token="44442")
            )

    # network error
    with domock(get_side_effect(raise_zeep_error=True)):
        with pytest.raises(GatewayNetworkError):
            gateway.verify_transaction(
                transaction, dict(OrderId="44441", Token="44442")
            )

    # no token
    with domock(get_side_effect(returned_token=None)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # zeep fault
    with domock(get_side_effect(raise_zeep_fault=True)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # network error
    with domock(get_side_effect(raise_zeep_error=True)):
        with pytest.raises(GatewayNetworkError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))
