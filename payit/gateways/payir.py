import json
from urllib import request, parse, error
from payit import Gateway, Transaction
from payit.exceptions import GatewayNetworkError, TransactionError
from payit.redirection import Redirection


class PayIrGateway(Gateway):
    """
    Pay.ir Gateway
    Home: https://pay.ir
    Documentation: https://pay.ir/developers/gateway-help
    """
    __gateway_name__ = 'payir'
    __gateway_unit__ = 'IRR'
    __config_params__ = ['pin', 'callback_url']

    def get_redirection(self, transaction) -> Redirection:
        return Redirection(
            url='https://pay.ir/payment/gateway/%s' % transaction.id,
            method='get'
        )

    def request_transaction(self, transaction: Transaction) -> Transaction:
        url = 'https://pay.ir/payment/send'
        data = {
            'api': self.config['pin'],
            'amount': transaction.amount,
            'redirect': self.config['callback_url']
        }
        if self.testing:  # pragma: nocover
            url = 'https://pay.ir/payment/test/send'
            data['api'] = 'test'

        try:
            req = request.Request(url, data=parse.urlencode(data).encode())
            resp = request.urlopen(req)
            resp = json.loads(resp.read().decode())
        except error.URLError:
            raise GatewayNetworkError('Cannot connect to payline server.')

        if resp['status'] == 1 and resp['transId']:
            transaction.id = resp['transId']
        else:
            raise TransactionError('%s, code: %s' % (resp['errorMessage'], resp['errorCode']))

        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        transaction = Transaction()
        transaction.id = data['transId']
        transaction.meta = data
        if int(data['status']) == 1:
            transaction.validate_status = True
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        url = 'https://pay.ir/payment/verify'
        data = {
            'api': self.config['pin'],
            'transId': transaction.id,
        }
        if self.testing:  # pragma: nocover
            url = 'https://pay.ir/payment/test/verify'
            data['api'] = 'test'

        try:
            req = request.Request(url, data=parse.urlencode(data).encode())
            resp = request.urlopen(req)
            resp = json.loads(resp.read().decode())
        except error.HTTPError as e:
            if e.code == 422:
                raise TransactionError('Invalid transaction id')
            raise TransactionError('Invalid transaction information')
        except error.URLError:
            raise GatewayNetworkError('Cannot connect to payline server.')

        if int(resp['status']) == 1:
            if int(transaction.amount) == int(resp['amount']):
                return transaction
            else:
                raise TransactionError('Amount mismatch')
        else:
            raise TransactionError('%s, code: %s' % (resp['errorMessage'], resp['errorCode']))
