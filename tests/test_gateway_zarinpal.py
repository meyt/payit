import pytest

from mock import patch

from payit import Transaction, TransactionError, GatewayNetworkError
from payit.gateways import ZarinpalGateway

from tests.mockup.zarinpal_gateway import get_side_effect


config = {
    "merchant": "534534534532225234234",
    "description": "",
    "callback_url": "http://localhost/callback",
    "proxies": "socks5://127.0.0.1:9050",
}


def domock(sideeffect):
    return patch("payit.gateways.zarinpal.Client", side_effect=sideeffect)


def test_gateway():
    with domock(get_side_effect()):
        gateway = ZarinpalGateway(config=config)
        transaction = gateway.request_transaction(
            Transaction(amount=1000, order_id=1)
        )
        gateway.get_redirection(transaction)

        # validation
        valid_transaction = gateway.validate_transaction(
            {"Authority": "RETURNED_TOKEN", "Status": "OK"}
        )
        assert valid_transaction.validate_status

        invalid_transaction = gateway.validate_transaction(
            {"Authority": "RETURNED_TOKEN", "Status": "NOK"}
        )
        assert not invalid_transaction.validate_status

    # success verification
    with domock(get_side_effect(returned_status=100)):
        gateway.verify_transaction(transaction, dict())

    # verification fails
    with domock(get_side_effect(returned_status=300)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # verification already done
    with domock(get_side_effect(returned_status=101)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, dict())

    # verification network error
    with domock(get_side_effect(raise_zeep_error=True)):
        with pytest.raises(GatewayNetworkError):
            gateway.verify_transaction(transaction, dict())

    # no token
    with domock(get_side_effect(returned_token=None)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # transation error
    with domock(get_side_effect(raise_zeep_fault=True)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # gateway error
    with domock(get_side_effect(raise_zeep_error=True)):
        with pytest.raises(GatewayNetworkError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))
