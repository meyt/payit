from requests import RequestException


def get_side_effect(
    returned_text=None,
    raise_url_error=False,
    http_status_code=200,
):
    def inner(*args, **kwargs):
        if raise_url_error:
            raise RequestException

        class Response:
            status_code = http_status_code
            text = returned_text

        return Response()

    return inner
