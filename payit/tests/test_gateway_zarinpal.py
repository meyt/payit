import mock
import unittest

from payit import Transaction, TransactionError, GatewayNetworkError
from payit.gateways import ZarinpalGateway
from payit.tests.mockup.zarinpal_gateway import get_side_effect


class ZarinpalGatewayTest(unittest.TestCase):
    _config = {
        'merchant': '534534534532225234234',
        'description': '',
        'callback_url': 'http://localhost/callback',
        'proxies': 'socks5://127.0.0.1:9050'
    }

    @mock.patch('payit.gateways.zarinpal.Client', side_effect=get_side_effect())
    def test_gateway(self, _):
        gateway = ZarinpalGateway(config=self._config)
        transaction = gateway.request_transaction(
            Transaction(
                amount=1000,
                order_id=1
            )
        )
        gateway.get_redirection(transaction)

        valid_transaction = gateway.validate_transaction({
            'Authority': 'RETURNED_TOKEN',
            'Status': 'OK'
        })
        self.assertEqual(valid_transaction.validate_status, True)

        invalid_transaction = gateway.validate_transaction({
            'Authority': 'RETURNED_TOKEN',
            'Status': 'NOK'
        })
        self.assertEqual(invalid_transaction.validate_status, False)

        @mock.patch('payit.gateways.zarinpal.Client', side_effect=get_side_effect(returned_status=100))
        def test_verify_success(_):
            gateway.verify_transaction(transaction, dict())
        test_verify_success()

        @mock.patch('payit.gateways.zarinpal.Client', side_effect=get_side_effect(returned_status=300))
        def test_verify_fail(_):
            with self.assertRaises(TransactionError):
                gateway.verify_transaction(transaction, dict())
        test_verify_fail()

        @mock.patch('payit.gateways.zarinpal.Client', side_effect=get_side_effect(returned_status=101))
        def test_verify_already_done(_):
            with self.assertRaises(TransactionError):
                gateway.verify_transaction(transaction, dict())
        test_verify_already_done()

        @mock.patch('payit.gateways.zarinpal.Client', side_effect=get_side_effect(raise_zeep_error=True))
        def test_verify_network_error(_):
            gateway.verify_transaction(transaction, dict())
        with self.assertRaises(GatewayNetworkError):
            test_verify_network_error()

    @mock.patch('payit.gateways.zarinpal.Client', side_effect=get_side_effect(returned_token=None))
    def test_no_token(self, _):
        gateway = ZarinpalGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch('payit.gateways.zarinpal.Client', side_effect=get_side_effect(raise_zeep_fault=True))
    def test_fault(self, _):
        gateway = ZarinpalGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch('payit.gateways.zarinpal.Client', side_effect=get_side_effect(raise_zeep_error=True))
    def test_error(self, _):
        gateway = ZarinpalGateway(config=self._config)
        with self.assertRaises(GatewayNetworkError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
