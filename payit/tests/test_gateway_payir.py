import mock
import unittest

from payit import Transaction, TransactionError, GatewayNetworkError
from payit.gateways import PayIrGateway
from payit.tests.mockup.payir_gateway import get_side_effect


class PayIrGatewayTest(unittest.TestCase):
    _config = {
        'pin': '8523528',
        'callback_url': 'http://localhost/callback'
    }
    _mock_request_path = 'payit.gateways.payir.request.Request'
    _mock_path = 'payit.gateways.payir.request.urlopen'

    @mock.patch(_mock_request_path)
    @mock.patch(_mock_path, side_effect=get_side_effect())
    def test_pay_ir(self, _, __):
        gateway = PayIrGateway(config=self._config)
        transaction = gateway.request_transaction(
            Transaction(
                amount=1000,
                order_id=1
            )
        )
        gateway.get_redirection(transaction)

        valid_transaction = gateway.validate_transaction({
            'transId': 'RETURNED_TOKEN',
            'status': '1'
        })
        self.assertEqual(valid_transaction.validate_status, True)

        invalid_transaction = gateway.validate_transaction({
            'transId': 'RETURNED_TOKEN',
            'status': '300'
        })
        self.assertEqual(invalid_transaction.validate_status, False)

        @mock.patch(self._mock_path, side_effect=get_side_effect(returned_status=1, returned_amount=1000))
        def test_verify_success(_):
            gateway.verify_transaction(transaction, dict())
        test_verify_success()

        @mock.patch(self._mock_path, side_effect=get_side_effect(returned_status=300, returned_amount=400))
        def test_verify_fail(_):
            gateway.verify_transaction(transaction, dict())
        with self.assertRaises(TransactionError):
            test_verify_fail()

        @mock.patch(self._mock_path, side_effect=get_side_effect(returned_status=1, returned_amount=600))
        def test_verify_mismatch_amount(_):
            gateway.verify_transaction(transaction, dict())
        with self.assertRaises(TransactionError):
            test_verify_mismatch_amount()

        @mock.patch(self._mock_path, side_effect=get_side_effect(raise_http_error=402))
        def test_verify_invalid_transaction(_):
            gateway.verify_transaction(transaction, dict())
        with self.assertRaises(TransactionError):
            test_verify_invalid_transaction()

        @mock.patch(self._mock_path, side_effect=get_side_effect(raise_http_error=422))
        def test_verify_invalid_transaction_id(_):
            gateway.verify_transaction(transaction, dict())

        with self.assertRaises(TransactionError):
            test_verify_invalid_transaction_id()

        @mock.patch(self._mock_path, side_effect=get_side_effect(raise_url_error=True))
        def test_verify_network_error(_):
            gateway.verify_transaction(transaction, dict())
        with self.assertRaises(GatewayNetworkError):
            test_verify_network_error()

    @mock.patch(_mock_path, side_effect=get_side_effect(returned_token=None))
    def test_no_token(self, _):
        gateway = PayIrGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch(_mock_path, side_effect=get_side_effect(raise_url_error=True))
    def test_error(self, _):
        gateway = PayIrGateway(config=self._config)
        with self.assertRaises(GatewayNetworkError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
