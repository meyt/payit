
import unittest

from mock import patch 

from payit import Transaction, TransactionError, GatewayNetworkError
from payit.gateways import BahamtaGateway
from payit.tests.mockup.bahamta_gateway import get_side_effect


class BahamtaGatewayTest(unittest.TestCase):
    _config = {
        'access_token': 'aabbbccdddeeff',
        'fund_id': '20',
        'number': '989090909090'
    }
    _mock_path = 'payit.gateways.bahamta.request'

    @patch(_mock_path, side_effect=get_side_effect())
    def test_bahamta(self, _):
        gateway = BahamtaGateway(config=self._config)
        transaction = gateway.request_transaction(
            Transaction(
                amount=1000,
                meta=dict(
                    payer_name='سهراب سپهری',
                    payer_number='989001234567',
                    note='عضویتِ ماهانه ی دی ماهِ ۹۳'
                )
            )
        )
        gateway.get_redirection(transaction)

        # Missed meta
        with self.assertRaises(ValueError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    meta=dict(
                        payer_name='سهراب سپهری',
                        note='عضویتِ ماهانه ی دی ماهِ ۹۳'
                    )
                )
            )

        # Request invalid transaction
        with self.assertRaises(TransactionError):
            with patch(
                self._mock_path,
                side_effect=get_side_effect(
                    http_status_code=400,
                    return_list=True
                )
            ):
                gateway.request_transaction(
                    Transaction(
                        amount=1000,
                        meta=dict(
                            payer_name='سهراب سپهری',
                            payer_number='989001234567',
                            note='عضویتِ ماهانه ی دی ماهِ ۹۳'
                        )
                    )
                )

        valid_transaction = gateway.validate_transaction({
            "fund_id": 20,
            "bill_id": 1,
            "code": "123456",
            "url": "https://bahamta.com/20/1-123456",
            "state": "pay",
            "amount": "1000",
            "created": "2015-03-02T12:57:58.123Z",
            "modified": "2015-03-02T12:57:58.123Z",
            "display": "2015-03-02T12:57:58.123Z",
            "payer_number": "989001234567",
            "payer_name": "سهراب سپهری",
            "fund_name": "صندوقِ آزمایشی",
            "iban": "IR123456789012345678901234",
            "account_owner": "سهراب سپهری",
            "note": "عضویتِ ماهانه ی دی ماهِ ۹۳",
            "pay_wage": "5000",
            "pay_trace": "11111",
            "pay_pan": "123456******1234",
            "transfer_estimate": "2015-03-03T05:30:00Z",
            "transfer_trace": "1234567890"
        })
        self.assertEqual(valid_transaction.validate_status, True)

        invalid_transaction = gateway.validate_transaction({
            "fund_id": 20,
            "bill_id": 1,
            "code": "123456",
            "url": "https://bahamta.com/20/1-123456",
            "state": "reject",
            "amount": "1000",
            "created": "2015-03-02T12:57:58.123Z",
            "modified": "2015-03-02T12:57:58.123Z",
            "display": "2015-03-02T12:57:58.123Z",
            "payer_number": "989001234567",
            "payer_name": "سهراب سپهری",
            "fund_name": "صندوقِ آزمایشی",
            "iban": "IR123456789012345678901234",
            "account_owner": "سهراب سپهری",
            "note": "عضویتِ ماهانه ی دی ماهِ ۹۳",
            "pay_wage": "5000",
            "pay_trace": "11111",
            "pay_pan": "123456******1234",
            "transfer_estimate": "2015-03-03T05:30:00Z",
            "transfer_trace": "1234567890"
        })
        self.assertEqual(invalid_transaction.validate_status, False)

        # Success verification
        with patch(
            self._mock_path,
            side_effect=get_side_effect(
                returned_status='pay',
                returned_amount=1000,
                return_list=False
            )
        ):
            gateway.verify_transaction(transaction, dict())

        with self.assertRaises(TransactionError):
            with patch(
                self._mock_path,
                side_effect=get_side_effect(
                    returned_status='reject',
                    returned_amount=400,
                    return_list=False
                )
            ):
                gateway.verify_transaction(transaction, dict())

        with self.assertRaises(TransactionError):
            with patch(
                self._mock_path,
                side_effect=get_side_effect(
                    returned_status='pay',
                    returned_amount=600,
                    return_list=False
                )
            ):
                gateway.verify_transaction(transaction, dict())

        with self.assertRaises(TransactionError):
            with patch(
                self._mock_path,
                side_effect=get_side_effect(
                    http_status_code=403,
                    return_list=False
                )
            ):
                gateway.verify_transaction(transaction, dict())

        with self.assertRaises(TransactionError):
            with patch(
                self._mock_path,
                side_effect=get_side_effect(
                    http_status_code=404,
                    return_list=False
                )
            ):
                gateway.verify_transaction(transaction, dict())

        with self.assertRaises(GatewayNetworkError):
            with patch(
                self._mock_path,
                side_effect=get_side_effect(
                    raise_url_error=True,
                    return_list=False
                )
            ):
                gateway.verify_transaction(transaction, dict())

    @patch(_mock_path, side_effect=get_side_effect(raise_url_error=True))
    def test_error(self, _):
        gateway = BahamtaGateway(config=self._config)
        with self.assertRaises(GatewayNetworkError):
            gateway.request_transaction(
                Transaction(
                    amount=1000,
                    meta=dict(
                        payer_name='سهراب سپهری',
                        payer_number='989001234567',
                        note='عضویتِ ماهانه ی دی ماهِ ۹۳'
                    )
                )
            )


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
