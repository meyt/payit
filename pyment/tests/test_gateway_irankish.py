import mock
import unittest

from pyment import Transaction, TransactionError, GatewayNetworkError
from pyment.gateways import IrankishGateway
from pyment.tests.mockup.irankish_gateway import get_side_effect


class IrankishGatewayTest(unittest.TestCase):
    _config = {
        'merchant': 'C0C1',
        'sha1key': '212320992352934514917221765200141041845518824222260',
        'callback_url': 'http://localhost/callback',
        'proxies': 'socks5://127.0.0.1:9050'
    }

    @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect())
    def test_gateway(self, _):
        gateway = IrankishGateway(config=self._config)
        transaction = gateway.request_transaction(
            Transaction(
                amount=1000,
                order_id=1
            )
        )
        gateway.get_redirection(transaction)

        valid_transaction = gateway.validate_transaction({
            'token': 'RETURNED_TOKEN',
            'resultCode': '100'
        })
        self.assertEqual(valid_transaction.validate_status, True)

        invalid_transaction = gateway.validate_transaction({
            'token': 'RETURNED_TOKEN',
            'resultCode': '300'
        })
        self.assertEqual(invalid_transaction.validate_status, False)

        @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect(verify_result=1000))
        def test_verify_success(_):
            gateway.verify_transaction(transaction, dict())
        test_verify_success()

        @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect())
        def test_verify_fail(_):
            with self.assertRaises(TransactionError):
                gateway.verify_transaction(transaction, dict())
        test_verify_fail()

        @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect(verify_result=-90))
        def test_verify_already_done(_):
            with self.assertRaises(TransactionError):
                gateway.verify_transaction(transaction, dict())
        test_verify_already_done()

        @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect(verify_result=-900))
        def test_verify_unknown_error(_):
            with self.assertRaises(TransactionError):
                gateway.verify_transaction(transaction, dict())
        test_verify_unknown_error()

        @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect(raise_zeep_error=True))
        def test_verify_network_error(_):
            with self.assertRaises(TransactionError):
                gateway.verify_transaction(transaction, dict())
        with self.assertRaises(GatewayNetworkError):
            test_verify_network_error()

    @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect(returned_token=None))
    def test_no_token(self, _):
        gateway = IrankishGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect(raise_zeep_fault=True))
    def test_fault(self, _):
        gateway = IrankishGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch('pyment.gateways.irankish.Client', side_effect=get_side_effect(raise_zeep_error=True))
    def test_error(self, _):
        gateway = IrankishGateway(config=self._config)
        with self.assertRaises(GatewayNetworkError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

if __name__ == '__main__':  # pragma: nocover
    unittest.main()
