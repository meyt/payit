from requests import request, RequestException

from payit import (
    Gateway,
    Transaction,
    Redirection,
    GatewayNetworkError,
    TransactionError,
)


class PayIrGateway(Gateway):
    """
    Pay.ir Gateway

    Home: https://pay.ir
    Documentation: https://pay.ir/docs/gateway/
    Last Modification: 2022-02-26
    """

    __gateway_name__ = "payir"
    __gateway_unit__ = "IRR"
    __config_params__ = ["pin", "callback_url"]

    _request_error_map = {
        "-1": "ApiKeyNotFound",
        "-2": "AmountNotFound",
        "-3": "AmountNotInteger",
        "-4": "AmountNotCorrect",
        "-5": "RedirectUrlNotFound",
        "-6": "PaymentGatewayNotFound",
        "-7": "SellerNotActive",
        "-8": "RedirectUrlsNotMatching",
        "failed": "TransactionFailed",
    }

    _verify_error_map = {
        "-1": "ApiKeyNotFound",
        "-2": "TransIdNotFound",
        "-3": "PaymentGatewayNotFound",
        "-4": "SellerNotActive",
        "-5": "TransactionFailed",
    }

    def get_redirection(self, transaction) -> Redirection:
        return Redirection(
            url="https://pay.ir/pg/%s" % transaction.id,
            method="get",
        )

    def request_transaction(self, transaction: Transaction) -> Transaction:
        url = "https://pay.ir/pg/send"
        formdata = {
            "api": "test" if self.testing else self.config["pin"],
            "amount": transaction.amount,
            "redirect": self.config["callback_url"],
        }

        if transaction.order_id:
            formdata["factorNumber"] = transaction.order_id

        optional_fields = (
            "mobile",
            "validCardNumber",
            "description",
        )
        for field in optional_fields:
            if field not in transaction.meta:
                continue
            formdata[field] = transaction.meta[field]

        try:
            resp = request("post", url, data=formdata)
        except RequestException:
            raise GatewayNetworkError("Cannot connect to payir server")

        try:
            body = resp.json()
        except Exception:
            body = None

        if resp.status_code != 200:
            if not body:
                raise TransactionError(
                    "Invalid transaction information (%s)" % resp.status_code
                )

            raise TransactionError(
                "%s, code: %s" % (body["errorMessage"], body["errorCode"])
            )

        transaction.id = body["token"]
        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        transaction = Transaction()
        transaction.id = data["token"]
        transaction.meta = data
        transaction.validate_status = int(data["status"]) == 1
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        url = "https://pay.ir/pg/verify"
        formdata = {
            "api": "test" if self.testing else self.config["pin"],
            "token": transaction.id,
        }
        try:
            resp = request("post", url, data=formdata)
        except RequestException:
            raise GatewayNetworkError("Cannot connect to payir server")

        try:
            body = resp.json()
        except Exception:
            body = None

        if resp.status_code != 200:
            if not body:
                raise TransactionError(
                    "Invalid transaction information (%s)" % resp.status_code
                )

            raise TransactionError(
                "%s, code: %s" % (body["errorMessage"], body["errorCode"])
            )

        if int(transaction.amount) != int(body["amount"]):
            raise TransactionError("Amount mismatch")

        transaction.pan = body["cardNumber"]
        transaction.amount = int(body["amount"])
        transaction.order_id = body["factorNumber"]
        transaction.meta = body
        return transaction
