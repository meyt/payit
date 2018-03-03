import unittest

from payit import GatewayManager, Transaction, Gateway, GatewayManagerTesting


class DummyGateway(Gateway):

    def get_redirection(self, transaction: Transaction):  # pragma: nocover
        pass

    def request_transaction(self, transaction: Transaction):  # pragma: nocover
        pass

    def validate_transaction(self, data: dict):  # pragma: nocover
        pass

    def verify_transaction(self, transaction: Transaction, data):  # pragma: nocover
        pass


class GatewayManagerTest(unittest.TestCase):

    def test_gateway_manager(self):
        manager = GatewayManager()
        manager.register('dummy_gateway1', DummyGateway)
        manager.configure({'dummy_gateway1': {}})

        with self.assertRaises(ValueError):
            manager.configure({'dummy_gateway2': {}})

        transaction = Transaction(
            amount=1000,
            order_id=1,
            meta=dict(
                card_number='xyz'
            )
        )
        transaction = manager.request('dummy_gateway1', transaction)
        manager.validate('dummy_gateway1', {})
        manager.verify('dummy_gateway1', transaction, {})
        manager.get_redirection('dummy_gateway1', transaction)

        manager = GatewayManagerTesting()
        manager.register('dummy_gateway1', DummyGateway)
        manager.configure({'dummy_gateway1': {}})


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
