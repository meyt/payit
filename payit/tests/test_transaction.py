import unittest

from payit import Transaction


class TransactionTest(unittest.TestCase):

    def test_transaction(self):
        transaction = Transaction(
            amount=1000,
            order_id=1,
            meta=dict(
                card_number='xyz'
            )
        )
        transaction_dict = transaction.to_dict()
        self.assertEqual(transaction_dict['amount'], transaction.amount)


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
