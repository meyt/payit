import mock

from zeep import exceptions


def get_side_effect(
        returned_token='0,4444',
        returned_status=0,
        raise_zeep_fault=False,
        raise_zeep_error=False):
    # noinspection PyPep8Naming
    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    class Result:
        Token = returned_token
        Status = returned_status

    class ClientService:
        def SalePaymentRequest(self, *args, **kwargs):
            if raise_zeep_fault:
                raise exceptions.Fault('FAKE ZEEP FAULT')

            if raise_zeep_error:
                raise exceptions.Error('FAKE ZEEP ERROR')
            return Result

        def ConfirmPayment(self, *args, **kwargs):
            if raise_zeep_error:
                raise exceptions.Error('FAKE ZEEP ERROR')

            return Result

    class Client:
        service = ClientService()
        transport = mock.MagicMock()

        def __init__(self, *args, **kwargs):
            pass

    def side_effect(*args, **kwargs):
        return Client(*args, **kwargs)

    return side_effect
