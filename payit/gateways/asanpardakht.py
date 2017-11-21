import base64
from typing import List, Tuple
from datetime import datetime

from py3rijndael import RijndaelCbc, Pkcs7Padding

from zeep import Client, exceptions as zeep_exceptions

from payit import Gateway, Transaction
from payit.exceptions import GatewayNetworkError, TransactionError, TransactionAlreadyPaidError
from payit.redirection import Redirection


class AsanPardakhtGateway(Gateway):
    """
    Irankish
    Home: http://asanpardakht.ir/
    Documentation: http://asanpardakht.ir/ipgdownload/ipgdoc.pdf
    """
    __gateway_name__ = 'asan_pardakht'
    __gateway_unit__ = 'IRR'
    __config_params__ = [
        'key',
        'iv',
        'username',
        'password',
        'merchant_config_id',
        'callback_url',
        'proxies'
    ]
    _server_url = 'https://services.asanpardakht.net/paygate/merchantservices.asmx?WSDL'

    def __init__(self, config):
        super().__init__(config)
        self.rijndael = RijndaelCbc(
            key=base64.b64decode(config['key']),
            iv=base64.b64decode(config['iv']),
            padding=Pkcs7Padding(32),
            block_size=32
        )

    def _get_request_payload(
            self,
            transaction: Transaction,
            additional_data: str='',
            accounts: List[Tuple[str, str]]=None
    ):
        """
        Get request payload
        :param transaction: 
        :param additional_data: 
        :param accounts: More (Shaba) accounts, Maximum 7 accounts can use. 
               eg: [('shaba1', '100'), ('shaba2', '200'))]
        :return: 
        """
        accounts = [n for account in accounts for n in account] if accounts else []
        return [
            '1',
            self.config['username'],
            self.config['password'],
            str(transaction.order_id),
            str(transaction.amount),
            datetime.now().strftime('%Y%m%d %I%M%S'),
            additional_data,  # Additional data maximum length is 100 characters
            self.config['callback_url'],
            '0'  # Payment id (optional)
        ] + accounts

    def _get_encrypted_request(self, transaction: Transaction):
        return base64.b64encode(
            self.rijndael.encrypt(
                ','.join(self._get_request_payload(transaction)).encode()
            )
        )

    def _parse_callback_data(self, data: dict):
        data = self.rijndael.decrypt(
            base64.b64decode(data['ReturningParams'])
        ).decode()
        exploded_data = data.split(',')
        return dict(
            amount=exploded_data[0],  # Transaction amount
            sale_order_id=exploded_data[1],  # Transaction Order ID
            ref_id=exploded_data[2],  # Transaction ID
            res_code=exploded_data[3],  # Result Code
            res_message=exploded_data[4],  # Result Message
            pay_gate_trans_id=exploded_data[5],  # Transaction inquiry id
            rrn=exploded_data[6],  # Bank Reference ID
            last_four_digit_of_pan=exploded_data[7],  # Last four digits of payer card ID
        )

    @property
    def _encrypted_credentials(self):
        return base64.b64encode(
            self.rijndael.encrypt(
                ','.join([self.config['username'], self.config['password']]).encode()
            )
        )

    def get_redirection(self, transaction) -> Redirection:
        return Redirection(
            url='https://asan.shaparak.ir/',
            body_params=dict(RefId=transaction.id, RedirctToIPGFORM='true'),
            method='post'
        )

    def request_transaction(self, transaction: Transaction) -> Transaction:
        client = Client(self._server_url)
        if 'proxies' in self.config:
            client.transport.session.proxies = self.config['proxies']
        try:
            params = {
                'merchantConfigurationID': self.config['merchant_config_id'],
                'encryptedRequest': self._get_encrypted_request(transaction)
            }

            result = client.service.RequestOperation(**params)
            if not result:
                raise TransactionError('AsanPardakht: invalid information.')

            if result[0:1] == '0':
                exploded_result = str(result).split(',')  # Should have two part [XX,YY]
                transaction.id = exploded_result[1]
            else:
                raise TransactionError('AsanPardakht: invalid information. code: %s' % str(result))

        except zeep_exceptions.Fault:
            raise TransactionError('AsanPardakht: invalid information.')

        except zeep_exceptions.Error:
            raise GatewayNetworkError

        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        parsed_data = self._parse_callback_data(data)
        transaction = Transaction()
        transaction.id = parsed_data['ref_id']
        transaction.meta = parsed_data
        if int(parsed_data['res_code']) == 0:
            transaction.validate_status = True
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        try:
            parsed_data = self._parse_callback_data(data)
            params = {
                'merchantConfigurationID': int(self.config['merchant_config_id']),
                'encryptedCredentials': self._encrypted_credentials,
                'payGateTranID': parsed_data['pay_gate_trans_id']
            }
            client = Client(self._server_url)
            if 'proxies' in self.config:
                client.transport.session.proxies = self.config['proxies']

            verify_result = int(client.service.RequestVerification(**params))
            if verify_result == 505:
                raise TransactionAlreadyPaidError('AsanPardakht: transaction already verified')
            elif verify_result != 500:
                raise TransactionError('AsanPardakht: invalid transaction, %s' % verify_result)

            reconcile_result = int(client.service.RequestReconciliation(**params))
            if reconcile_result != 600:
                raise TransactionError('AsanPardakht: invalid transaction settlement, %s' % reconcile_result)

        except zeep_exceptions.Error:
            raise GatewayNetworkError

        return transaction
