import mock
import unittest

from payit import Transaction, TransactionError, GatewayNetworkError
from payit.gateways import ParsianGateway
from payit.tests.mockup.parsian_gateway import get_side_effect


class ParsianGatewayTest(unittest.TestCase):
    _config = {
        'pid': '1234',
        'callback_url': 'http://localhost/callback',
        'proxies': 'socks5://127.0.0.1:9050'
    }

    @mock.patch('payit.gateways.parsian.Client',
                side_effect=get_side_effect(returned_token='4444'))
    def test_gateway(self, _):
        gateway = ParsianGateway(config=self._config)
        transaction = gateway.request_transaction(
            Transaction(
                amount=1000,
                order_id=1
            )
        )
        gateway.get_redirection(transaction)

        valid_transaction = gateway.validate_transaction({
            'Token': '4444',
            'Status': '0'
        })
        self.assertEqual(valid_transaction.validate_status, True)

        invalid_transaction = gateway.validate_transaction({
            'Token': '4444',
            'Status': '300'
        })
        self.assertEqual(invalid_transaction.validate_status, False)

        @mock.patch('payit.gateways.parsian.Client',
                    side_effect=get_side_effect(returned_status=0))
        def test_verify_success(_):
            gateway.verify_transaction(transaction, dict(
                OrderId='44441',
                Token='44442'
            ))
        test_verify_success()

        @mock.patch('payit.gateways.parsian.Client',
                    side_effect=get_side_effect(returned_status=-100))
        def test_verify_fail(_):
            gateway.verify_transaction(transaction, dict(
                OrderId='44441',
                Token='44442'
            ))
        with self.assertRaises(TransactionError):
            test_verify_fail()

        @mock.patch('payit.gateways.parsian.Client',
                    side_effect=get_side_effect(returned_status=-1533))
        def test_already_verified(_):
            gateway.verify_transaction(transaction, dict(
                OrderId='44441',
                Token='44442'
            ))
        with self.assertRaises(TransactionError):
            test_already_verified()

        @mock.patch('payit.gateways.parsian.Client',
                    side_effect=get_side_effect(raise_zeep_error=True))
        def test_verify_network_error(_):
            gateway.verify_transaction(transaction, dict(
                OrderId='44441',
                Token='44442'
            ))

        with self.assertRaises(GatewayNetworkError):
            test_verify_network_error()

    @mock.patch('payit.gateways.parsian.Client',
                side_effect=get_side_effect(returned_token=None))
    def test_no_token(self, _):
        gateway = ParsianGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch('payit.gateways.parsian.Client',
                side_effect=get_side_effect(raise_zeep_fault=True))
    def test_fault(self, _):
        gateway = ParsianGateway(config=self._config)
        with self.assertRaises(TransactionError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )

    @mock.patch('payit.gateways.parsian.Client',
                side_effect=get_side_effect(raise_zeep_error=True))
    def test_error(self, _):
        gateway = ParsianGateway(config=self._config)
        with self.assertRaises(GatewayNetworkError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    order_id=1
                )
            )


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
