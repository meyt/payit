import mock

from zeep import exceptions


def get_side_effect(
    returned_token="0,RETURNED_TOKEN",
    verify_result=500,
    reconcile_result=600,
    raise_zeep_fault=False,
    raise_zeep_error=False,
):
    # noinspection PyPep8Naming
    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal

    class ClientService:
        @staticmethod
        def RequestOperation(merchantConfigurationID, encryptedRequest):
            token = returned_token

            if raise_zeep_fault:
                raise exceptions.Fault("FAKE ZEEP FAULT")

            if raise_zeep_error:
                raise exceptions.Error("FAKE ZEEP ERROR")
            return token

        @staticmethod
        def RequestVerification(
            merchantConfigurationID, encryptedCredentials, payGateTranID
        ):
            if raise_zeep_error:
                raise exceptions.Error("FAKE ZEEP ERROR")

            return verify_result

        @staticmethod
        def RequestReconciliation(
            merchantConfigurationID, encryptedCredentials, payGateTranID
        ):
            if raise_zeep_error:  # pragma: nocover
                raise exceptions.Error("FAKE ZEEP ERROR")

            return reconcile_result

    class Client:
        service = ClientService()
        transport = mock.MagicMock()

        def __init__(self, *args, **kwargs):
            pass

    def side_effect(*args, **kwargs):
        return Client(*args, **kwargs)

    return side_effect
