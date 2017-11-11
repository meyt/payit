from urllib import error
import json


def get_side_effect(
        returned_token='RETURNED_TOKEN',
        returned_amount=100,
        returned_status=1,
        error_message=None,
        error_code=None,
        raise_url_error=False,
        raise_http_error=False):
    # noinspection PyUnusedLocal

    def urlopen(*args, **kwargs):
        if raise_url_error:
            raise error.URLError('FAKE ERROR')

        if raise_http_error:
            raise error.HTTPError(url='', code=raise_http_error, msg='FAKE ERROR', hdrs={}, fp=None)

        class Response:
            @staticmethod
            def read():
                return json.dumps(
                    {
                        'transId': returned_token,
                        'status': returned_status,
                        'amount': returned_amount,
                        'errorMessage': error_message,
                        'errorCode': error_code
                    }
                ).encode()

        return Response()
    return urlopen
