from requests import request, RequestException

from payit import (
    Gateway,
    Transaction,
    Redirection,
    GatewayNetworkError,
    TransactionError,
)


class BahamtaGateway(Gateway):
    """
    Bahamta Gateway

    Bahamta have little different behavior than other gateways,

    It need more extra fields to create new transaction (described below)
    and does not redirect client to your site.

    Bahamta calls callback URL on any change happen on bills.
    callback contains multiple bills/transactions, you need to separate those
    bills/transactions and then validate/verify each one.

    Input meta keys on request new transaction:
    - payer_name (required)
    - payer_number (required)
    - note (required)
    - silent (optional)

    Home: https://bahamta.com
    Documentation: https://api.bahamta.com/v2/
    """

    __gateway_name__ = "bahamta"
    __gateway_unit__ = "IRR"
    __config_params__ = ["access_token", "fund_id", "number"]

    @property
    def _server_url(self):
        return "https://api.bahamta.com/v2/%s/funds/%s" % (
            self.config["number"],
            self.config["fund_id"],
        )

    def get_redirection(self, transaction) -> Redirection:
        return Redirection(url=transaction.meta["url"], method="get")

    def request_transaction(self, transaction: Transaction) -> Transaction:
        data = {
            "payer_number": transaction.meta.get("payer_number"),
            "payer_name": transaction.meta.get("payer_name"),
            "amount": transaction.amount,
            "note": transaction.meta.get("note"),
            "silent": transaction.meta.get("silent"),
        }
        for key in ("payer_name", "payer_number", "note"):
            if data[key] is None:
                raise ValueError("Transaction meta required (%s)" % key)
        url = "%s/bills" % self._server_url
        headers = {
            "access-token": self.config["access_token"],
            "content-type": "application/json",
        }
        try:
            response = request("post", url, json=[data], headers=headers)
        except RequestException:
            raise GatewayNetworkError("Cannot connect to bahamta server.")

        if response.status_code != 200:
            raise TransactionError(
                "Invalid transaction information (%s)" % response.status_code
            )
        response_data = response.json()[0]
        transaction.id = response_data["bill_id"]
        transaction.meta = response_data
        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        transaction = Transaction()
        transaction.id = data["bill_id"]
        transaction.meta = data
        if data["state"] in ("pay", "request"):
            transaction.validate_status = True
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        url = "%s/bills/%s" % (self._server_url, transaction.id)
        headers = {
            "access-token": self.config["access_token"],
            "content-type": "application/json",
        }
        try:
            response = request("get", url, headers=headers)
        except RequestException:
            raise GatewayNetworkError("Cannot connect to bahamta server.")

        if response.status_code != 200:
            raise TransactionError(
                "Invalid transaction information (%s)" % response.status_code
            )
        response_data = response.json()

        if response_data["state"] != "pay":
            raise TransactionError("Transaction not paid")

        if int(transaction.amount) != int(response_data["amount"]):
            raise TransactionError("Amount mismatch")

        transaction.pan = response_data["pay_pan"]
        transaction.meta = response_data
        return transaction
