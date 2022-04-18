from requests import request, RequestException

from payit import (
    Gateway,
    Transaction,
    Redirection,
    GatewayNetworkError,
    TransactionError,
    TransactionAlreadyPaidError,
)
from payit.helpers import irr_to_irt


class AqayepardakhtGateway(Gateway):
    """
    Aqayepardakht Gateway

    Home: https://aqayepardakht.ir/
    Documentation: https://aqayepardakht.ir/api/
    Last Modification: 2022-02-26
    """

    __gateway_name__ = "aqayepardakht"
    __gateway_unit__ = "IRR"
    __config_params__ = ["pin", "callback_url"]
    _server_url = "https://panel.aqayepardakht.ir/api"
    _verify_status_map = {
        "2": "already verified",
        "1": "paid",
        "0": "not paid",
        "-1": "amount is empty",
        "-2": "pin is empty",
        "-3": "callback is empty",
        "-4": "amount is not numeric",
        "-5": "amount is less than minimum (100)",
        "-6": "pin is invalid",
        "-7": "server ip mismatch",
        "-8": "transid is empty",
        "-9": "transaction not found",
        "-10": "transaction pin mismatch",
        "-11": "transaction amount mismatch",
        "-12": "invalid bank",
        "-13": "inactive gateway",
        "-14": "gateway already used",
    }

    def get_redirection(self, transaction) -> Redirection:
        return Redirection(
            url="https://panel.aqayepardakht.ir/startpay/%s" % transaction.id,
            method="get",
        )

    def request_transaction(self, transaction: Transaction) -> Transaction:
        formdata = {
            "pin": self.config["pin"],
            "amount": irr_to_irt(transaction.amount),
            "callback": self.config["callback_url"],
        }
        optional_fields = (
            "card_number",
            "invoice_id",
            "mobile",
            "description",
        )
        for field in optional_fields:
            if field not in transaction.meta:
                continue
            formdata[field] = transaction.meta[field]

        try:
            response = request(
                method="post",
                url="%s/create" % self._server_url,
                data=formdata,
            )
        except RequestException:
            raise GatewayNetworkError("Cannot connect to aqayepardakht server")

        if response.status_code != 200:
            raise TransactionError(
                "Invalid transaction information (%s)" % response.status_code
            )

        transaction.id = response.text
        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        transaction = Transaction()
        transaction.id = data.get("transid")
        transaction.amount = int(data.get("amount", 0))
        transaction.pan = data.get("cardnumber")
        transaction.meta = data
        transaction.validate_status = transaction.id is not None
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        formdata = {
            "pin": self.config["pin"],
            "amount": transaction.amount,
            "transid": transaction.id,
        }

        try:
            response = request(
                method="post",
                url="%s/verify" % self._server_url,
                data=formdata,
            )

        except RequestException:
            raise GatewayNetworkError("Cannot connect to aqayepardakht server")

        if response.status_code != 200:
            raise TransactionError(
                "Invalid transaction information (%s)" % response.status_code
            )

        if response.text == "2":
            raise TransactionAlreadyPaidError

        if response.text != "1":
            raise TransactionError(
                self._verify_status_map.get(
                    response.text.strip(), "Transaction not paid"
                )
            )

        return transaction
