import mock

from zeep import exceptions


def get_side_effect(
    returned_token="0,4444",
    verify_result=0,
    settle_result=0,
    reversal_result=0,
    raise_zeep_fault=False,
    raise_zeep_error=False,
):
    # noinspection PyPep8Naming
    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal

    class ClientService:
        def bpPayRequest(self, *args, **kwargs):
            if raise_zeep_fault:
                raise exceptions.Fault("FAKE ZEEP FAULT")

            if raise_zeep_error:
                raise exceptions.Error("FAKE ZEEP ERROR")
            return returned_token

        def bpVerifyRequest(self, *args, **kwargs):
            if raise_zeep_error:
                raise exceptions.Error("FAKE ZEEP ERROR")

            return verify_result

        def bpReversalRequest(*args, **kwargs):
            return reversal_result

        def bpSettleRequest(*args, **kwargs):
            return settle_result

    class Client:
        service = ClientService()
        transport = mock.MagicMock()

        def __init__(self, *args, **kwargs):
            pass

    def side_effect(*args, **kwargs):
        return Client(*args, **kwargs)

    return side_effect
