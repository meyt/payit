from zeep import Client, exceptions as zeep_exceptions

from payit import (
    Gateway,
    Transaction,
    Redirection,
    GatewayNetworkError,
    TransactionError,
    TransactionAlreadyPaidError,
)


class IrankishGateway(Gateway):
    """
    Irankish

    Note: transaction.pan not supported.

    Home: https://www.irankish.com
    Documentation: http://www.kiccc.com/App_Data_Public/downloads/%D8%B1%D8%A7%D9%87%D9%86%D9%85%D8%A7%DB%8C%20%D9%81%D9%86%DB%8C%20%D9%81%D8%A7%D8%B1%D8%B3%DB%8C.pdf
    """

    __gateway_name__ = "irankish"
    __gateway_unit__ = "IRR"
    __config_params__ = ["merchant", "sha1key", "callback_url", "proxies"]
    _server_url_request = "https://ikc.shaparak.ir/XToken/Tokens.xml"
    _server_url_verify = "https://ikc.shaparak.ir/XVerify/Verify.xml"

    # This messages is just for prevent you from
    # headaches of reading current bad written documentation.
    _validate_response_messages = {
        "100": "success",
        "110": "payer cancelled",
        "120": "not enough credit",
        "130": "wrong card information",
        "131": "wrong card password",
        "132": "banned card",
        "133": "expired card",
        "140": "session timeout",
        "150": "gateway internal error",
        "160": "invalid cvv2 or expDate",
        "166": "card provider bank does not allow to make transaction",
        "200": "amount is greater than maximum range per transaction",
        "201": "amount is greater than maximum range per day",
        "202": "amount is greater than maximum range per month",
    }
    _verify_response_messages = {
        "-20": "invalid characters in request",
        "-30": "already reversed",
        "-50": "long request",
        "-51": "request error",
        "-80": "transaction not found",
        "-81": "gateway internal error",
        "-90": "already verified",
    }

    def get_redirection(self, transaction) -> Redirection:
        return Redirection(
            url="https://ikc.shaparak.ir/TPayment/Payment/index",
            body_params=dict(
                token=transaction.id,
                merchantId=self.config["merchant"],
                pay="submit",
            ),
            method="post",
        )

    def request_transaction(self, transaction: Transaction) -> Transaction:
        client = Client(self._server_url_request)
        if "proxies" in self.config:
            client.transport.session.proxies = self.config["proxies"]
        try:
            params = {
                "merchantId": self.config["merchant"],
                "invoiceNo": transaction.order_id,
                "paymentId": transaction.order_id,
                "specialPaymentId": transaction.order_id,
                "amount": int(transaction.amount),
                "description": "",
                "revertURL": self.config["callback_url"],
            }
            result = client.service.MakeToken(**params)
            token = result.token
            if token:
                transaction.id = token
            else:
                raise TransactionError("Irankish: invalid information.")

        except zeep_exceptions.Fault:
            raise TransactionError("Irankish: invalid information.")

        except zeep_exceptions.Error:
            raise GatewayNetworkError

        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        transaction = Transaction()
        transaction.id = data["token"]
        transaction.meta = data
        if "resultCode" in data and int(data["resultCode"]) == 100:
            transaction.validate_status = True
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        try:
            params = {
                "merchantId": self.config["merchant"],
                "referenceNumber": data["referenceId"]
                if "referenceId" in data
                else 0,
                "sha1Key": self.config["sha1key"],
                "token": transaction.id,
            }
            client = Client(self._server_url_verify)
            if "proxies" in self.config:
                client.transport.session.proxies = self.config["proxies"]

            result = int(client.service.KicccPaymentsVerification(**params))
            if result > 0:
                if result != float(transaction.amount):
                    raise TransactionError(
                        "Irankish: invalid transaction, amount mismatch"
                    )
            elif result == -90:
                raise TransactionAlreadyPaidError(
                    "Irankish: transaction already verified"
                )
            else:
                raise TransactionError(
                    "Irankish: invalid transaction, %s" % result
                )
        except zeep_exceptions.Error:
            raise GatewayNetworkError

        return transaction
