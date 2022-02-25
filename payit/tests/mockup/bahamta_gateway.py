from requests import RequestException


def get_side_effect(
    returned_id=1,
    returned_amount=100,
    returned_status="request",
    return_list=True,
    raise_url_error=False,
    http_status_code=200,
):
    # noinspection PyUnusedLocal

    def urlopen(*args, **kwargs):
        if raise_url_error:
            raise RequestException

        class Response:
            status_code = http_status_code

            @staticmethod
            def json():
                data = {
                    "fund_id": 20,
                    "bill_id": returned_id,
                    "code": "123456",
                    "url": "https://bahamta.com/20/1-123456",
                    "state": returned_status,
                    "amount": returned_amount,
                    "created": "2015-03-02T12:57:58.123Z",
                    "modified": "2015-03-02T12:57:58.123Z",
                    "display": "2015-03-02T12:57:58.123Z",
                    "payer_number": "989001234567",
                    "payer_name": "سهراب سپهری",
                    "fund_name": "صندوقِ آزمایشی",
                    "iban": "IR123456789012345678901234",
                    "account_owner": "سهراب سپهری",
                    "note": "عضویتِ ماهانه ی دی ماهِ ۹۳",
                    "pay_wage": "0",
                    "pay_trace": "",
                    "pay_pan": "",
                    "transfer_estimate": None,
                    "transfer_trace": "",
                }
                return [data] if return_list else data

        return Response()

    return urlopen
