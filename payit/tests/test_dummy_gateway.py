import unittest

from payit import Transaction, TransactionError
from payit.gateways import DummyGateway


class DummyGatewayTest(unittest.TestCase):
    _config = {
        "pin": "8523528",
        "callback_url": "http://localhost/callback",
        "maximum_amount": 150,
    }

    def test_dummy_gateway(self):
        gateway = DummyGateway(config=self._config)
        transaction = gateway.request_transaction(Transaction(amount=10))
        gateway.get_redirection(transaction)

        valid_transaction = gateway.validate_transaction(
            {"id": transaction.id, "validateStatus": True}
        )
        self.assertEqual(valid_transaction.validate_status, True)

        invalid_transaction = gateway.validate_transaction(
            {"id": transaction.id, "validateStatus": False}
        )
        self.assertEqual(invalid_transaction.validate_status, False)

        gateway.verify_transaction(transaction, dict(id=transaction.id))

        with self.assertRaises(TransactionError):
            gateway.verify_transaction(transaction, dict(id="false"))

        with self.assertRaises(TransactionError):
            gateway.request_transaction(Transaction(amount=15220))


if __name__ == "__main__":  # pragma: nocover
    unittest.main()
