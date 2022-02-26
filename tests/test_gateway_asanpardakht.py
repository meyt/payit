import mock
import base64
import pytest

from py3rijndael import RijndaelCbc, Pkcs7Padding

from payit import (
    Transaction,
    TransactionError,
    GatewayNetworkError,
    TransactionAlreadyPaidError,
)
from payit.gateways import AsanPardakhtGateway
from tests.mockup.asanpardakht_gateway import get_side_effect


config = {
    "key": "qBS8uRhEIBsr8jr8vuY9uUpGFefYRL2HSTtrKhaI1tk=",
    "iv": "kByhT6PjYHzJzZfXvb8Aw5URMbQnk6NM+g3IV5siWD4=",
    "username": "Test1258586",
    "password": "5T6Y7U8I",
    "merchant_config_id": "1460",
    "callback_url": "http://localhost/callback",
    "proxies": "socks5://127.0.0.1:9050",
}


def domock(sideeffect):
    return mock.patch(
        "payit.gateways.asanpardakht.Client", side_effect=sideeffect
    )


def generate_callback_data(
    amount=100,
    sale_order_id=1,
    ref_id=1,
    res_code=1,
    res_message=1,
    pay_gate_trans_id=1,
    rrn=1,
    last_four_digit_of_pan=1,
):
    rijndael = RijndaelCbc(
        key=base64.b64decode(config["key"]),
        iv=base64.b64decode(config["iv"]),
        padding=Pkcs7Padding(32),
        block_size=32,
    )
    data_array = [
        str(amount),  # Transaction amount
        str(sale_order_id),  # Transaction Order ID
        str(ref_id),  # Transaction ID
        str(res_code),  # Result Code
        str(res_message),  # Result Message
        str(pay_gate_trans_id),  # Transaction inquiry id
        str(rrn),  # Bank Reference ID
        str(last_four_digit_of_pan),  # Last four digits of payer card ID
    ]
    return {
        "ReturningParams": base64.b64encode(
            rijndael.encrypt(",".join(data_array).encode())
        )
    }


def test_gateway():
    gateway = AsanPardakhtGateway(config=config)
    with domock(get_side_effect()):
        transaction = gateway.request_transaction(
            Transaction(amount=1000, order_id=1)
        )
        gateway.get_redirection(transaction).to_dict()

        valid_transaction = gateway.validate_transaction(
            generate_callback_data(amount=1000, sale_order_id=1, res_code=0)
        )
        assert valid_transaction.validate_status

        invalid_transaction = gateway.validate_transaction(
            generate_callback_data(amount=1000, sale_order_id=1, res_code=300)
        )
        assert not invalid_transaction.validate_status

    # failed request
    with domock(get_side_effect(returned_token="300")):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # success verification
    with domock(get_side_effect(verify_result=500)):
        gateway.verify_transaction(transaction, generate_callback_data())

    # failed verification
    with domock(get_side_effect(verify_result=100)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, generate_callback_data())

    # reconcile fail
    with domock(get_side_effect(reconcile_result=300)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, generate_callback_data())

    # already paid
    with domock(get_side_effect(verify_result=505)):
        with pytest.raises(TransactionAlreadyPaidError):
            gateway.verify_transaction(transaction, generate_callback_data())

    # unknown error
    with domock(get_side_effect(verify_result=-900)):
        with pytest.raises(TransactionError):
            gateway.verify_transaction(transaction, generate_callback_data())

    # network error
    with domock(get_side_effect(raise_zeep_error=True)):

        with pytest.raises(GatewayNetworkError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))
        with pytest.raises(GatewayNetworkError):
            gateway.verify_transaction(transaction, generate_callback_data())

    # no token
    with domock(get_side_effect(returned_token=None)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))

    # zeep fault
    with domock(get_side_effect(raise_zeep_fault=True)):
        with pytest.raises(TransactionError):
            gateway.request_transaction(Transaction(amount=1000, order_id=1))
