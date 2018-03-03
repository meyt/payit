import mock

from zeep import exceptions


def get_side_effect(
        returned_token='RETURNED_TOKEN',
        verify_result=1,
        raise_zeep_fault=False,
        raise_zeep_error=False):
    # noinspection PyPep8Naming
    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal

    class ClientService:
        class MakeToken:
            token = returned_token

            def __init__(self, *args, **kwargs):
                if raise_zeep_fault:
                    raise exceptions.Fault('FAKE ZEEP FAULT')

                if raise_zeep_error:
                    raise exceptions.Error('FAKE ZEEP ERROR')

        def KicccPaymentsVerification(self, *args, **kwargs):
            if raise_zeep_error:
                raise exceptions.Error('FAKE ZEEP ERROR')

            return verify_result

    class Client:
        service = ClientService()
        transport = mock.MagicMock()

        def __init__(self, *args, **kwargs):
            pass

    def side_effect(*args, **kwargs):
        return Client(*args, **kwargs)

    return side_effect
