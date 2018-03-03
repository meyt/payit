import mock
import base64
import unittest

from py3rijndael import RijndaelCbc, Pkcs7Padding

from payit import Transaction, TransactionError, GatewayNetworkError
from payit.gateways import AsanPardakhtGateway
from payit.tests.mockup.asanpardakht_gateway import get_side_effect


class AsanPardakhtGatewayTest(unittest.TestCase):
    _config = {
        'key': 'qBS8uRhEIBsr8jr8vuY9uUpGFefYRL2HSTtrKhaI1tk=',
        'iv': 'kByhT6PjYHzJzZfXvb8Aw5URMbQnk6NM+g3IV5siWD4=',
        'username': 'Test1258586',
        'password': '5T6Y7U8I',
        'merchant_config_id': '1460',
        'callback_url': 'http://localhost/callback',
        'proxies': 'socks5://127.0.0.1:9050'
    }

    def _generate_callback_data(
            self,
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
            key=base64.b64decode(self._config['key']),
            iv=base64.b64decode(self._config['iv']),
            padding=Pkcs7Padding(32),
            block_size=32
        )
        data_array = [
            str(amount),  # Transaction amount
            str(sale_order_id),  # Transaction Order ID
            str(ref_id),  # Transaction ID
            str(res_code),  # Result Code
            str(res_message),  # Result Message
            str(pay_gate_trans_id),  # Transaction inquiry id
            str(rrn),  # Bank Reference ID
            str(last_four_digit_of_pan)  # Last four digits of payer card ID
        ]
        return {
            'ReturningParams': base64.b64encode(
                rijndael.encrypt(
                    ','.join(data_array).encode()
                )
            )
        }

    @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect())
    def test_gateway(self, _):
        gateway = AsanPardakhtGateway(config=self._config)
        transaction = gateway.request_transaction(
            Transaction(
                amount=1000,
                order_id=1
            )
        )
        gateway.get_redirection(transaction).to_dict()

        valid_transaction = gateway.validate_transaction(self._generate_callback_data(
            amount=1000,
            sale_order_id=1,
            res_code=0
        ))
        self.assertEqual(valid_transaction.validate_status, True)

        invalid_transaction = gateway.validate_transaction(self._generate_callback_data(
            amount=1000,
            sale_order_id=1,
            res_code=300
        ))
        self.assertEqual(invalid_transaction.validate_status, False)

        @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(returned_token='300'))
        def test_request_fail(_):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )
        with self.assertRaises(TransactionError):
            test_request_fail()

        @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(verify_result=500))
        def test_verify_success(_):
            gateway.verify_transaction(transaction, self._generate_callback_data())
        test_verify_success()

        @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(verify_result=100))
        def test_verify_fail(_):
            gateway.verify_transaction(transaction, self._generate_callback_data())
        with self.assertRaises(TransactionError):
            test_verify_fail()

        @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(reconcile_result=300))
        def test_verify_reconcile_fail(_):
            gateway.verify_transaction(transaction, self._generate_callback_data())
        with self.assertRaises(TransactionError):
            test_verify_reconcile_fail()

        @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(verify_result=505))
        def test_verify_already_done(_):
            gateway.verify_transaction(transaction, self._generate_callback_data())
        with self.assertRaises(TransactionError):
            test_verify_already_done()

        @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(verify_result=-900))
        def test_verify_unknown_error(_):
            gateway.verify_transaction(transaction, self._generate_callback_data())
        with self.assertRaises(TransactionError):
            test_verify_unknown_error()

        @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(raise_zeep_error=True))
        def test_verify_network_error(_):
            gateway.verify_transaction(transaction, self._generate_callback_data())
        with self.assertRaises(GatewayNetworkError):
            test_verify_network_error()

    @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(returned_token=None))
    def test_no_token(self, _):
        gateway = AsanPardakhtGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(raise_zeep_fault=True))
    def test_fault(self, _):
        gateway = AsanPardakhtGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch('payit.gateways.asanpardakht.Client', side_effect=get_side_effect(raise_zeep_error=True))
    def test_error(self, _):
        gateway = AsanPardakhtGateway(config=self._config)
        with self.assertRaises(GatewayNetworkError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
