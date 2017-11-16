from zeep import Client, exceptions as zeep_exceptions
from payit import Gateway, Transaction
from payit.exceptions import GatewayNetworkError, TransactionError, TransactionAlreadyPaidError
from payit.redirection import Redirection


class ZarinpalGateway(Gateway):
    """
    Zarinpal Gateway
    Home: https://zarinpal.com
    Documentation: https://github.com/ZarinPal-Lab/Documentation-PaymentGateway/archive/master.zip
    """
    __gateway_name__ = 'zarinpal'
    __gateway_unit__ = 'IRR'
    __config_params__ = ['merchant', 'description', 'callback_url']
    _server_url = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'

    @staticmethod
    def _convert_iranian_rial_to_toman(amount):
        return int(amount / 10)

    def get_redirection(self, transaction) -> Redirection:
        return Redirection(
            url='https://www.zarinpal.com/pg/StartPay/%s' % transaction.id,
            method='get'
        )

    def request_transaction(self, transaction: Transaction) -> Transaction:
        client = Client(self._server_url)
        try:
            result = client.service.PaymentRequest(
                self.config['merchant'],
                self._convert_iranian_rial_to_toman(transaction.amount),
                self.config['description'],
                '',
                '',
                self.config['callback_url']
            )

        except zeep_exceptions.Fault:
            raise TransactionError('Zarinpal: invalid information')

        except zeep_exceptions.Error:
            raise GatewayNetworkError

        if result.Status == 100 and result.Authority:
            transaction.id = result.Authority
        else:
            raise TransactionError('Zarinpal: invalid information')

        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        transaction = Transaction()
        transaction.id = data['Authority']
        transaction.meta = data
        if data['Status'] == 'OK':
            transaction.validate_status = True
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        try:
            client = Client(self._server_url)
            result = client.service.PaymentVerification(
                self.config['merchant'],
                transaction.id,
                self._convert_iranian_rial_to_toman(transaction.amount)
            )
        except zeep_exceptions.Error:
            raise GatewayNetworkError

        if result.Status == 100:
            return transaction

        elif result.Status == 101:
            raise TransactionAlreadyPaidError

        else:
            raise TransactionError('code: %s' % result.Status)
