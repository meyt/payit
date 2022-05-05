import time

from payit import Gateway, Transaction, Redirection, TransactionError


class DummyGateway(Gateway):
    """
    Dummy Gateway

    """

    __gateway_name__ = "dummy"
    __gateway_unit__ = "IRR"
    __config_params__ = ["pin", "callback_url", "maximum_amount"]
    __base_url__ = "https://dummy-gateway.localhost"

    def _generate_id(self):
        return int(time.time())

    @property
    def maximum_amount(self) -> int:
        return int(self.config["maximum_amount"] or 1000000)

    def get_redirection(self, transaction) -> Redirection:
        result = Redirection(
            url="/".join((self.__class__.__base_url__, str(transaction.id))),
            method="get",
        )
        print("New redirection created: \n%s" % result.__repr__())
        return result

    def request_transaction(self, transaction: Transaction) -> Transaction:
        if int(transaction.amount) > self.maximum_amount:
            raise TransactionError(
                "Amount is larger than %s" % self.maximum_amount
            )

        transaction.id = self._generate_id()
        print("New transaction requested: \n%s" % transaction.__repr__())
        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        transaction = Transaction()
        transaction.id = data["id"]
        transaction.meta = data
        transaction.validate_status = data.get("validateStatus", True)
        print("Transaction validated: \n%s" % transaction.__repr__())
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        if data["id"] == "false":
            raise TransactionError("Invalid transaction ID")

        transaction.pan = data.get("cardNumber")
        print("Transaction verified: \n%s" % transaction.__repr__())
        return transaction
