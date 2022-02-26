from requests import RequestException


def get_side_effect(
    returned_token="RETURNED_TOKEN",
    returned_amount=100,
    returned_status=1,
    error_message=None,
    error_code=None,
    raise_url_error=False,
    http_status_code=200,
    invalid_json=False,
):
    def urlopen(*args, **kwargs):
        if raise_url_error:
            raise RequestException

        class Response:
            status_code = http_status_code

            @staticmethod
            def json():
                if invalid_json:
                    raise ValueError

                return {
                    "token": returned_token,
                    "transId": returned_token,
                    "cardNumber": "1111-2222-3333-4444",
                    "message": "OK",
                    "factorNumber": "112233",
                    "status": returned_status,
                    "amount": returned_amount,
                    "errorMessage": error_message,
                    "errorCode": error_code,
                }

        return Response()

    return urlopen
