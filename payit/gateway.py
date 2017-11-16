from . import Transaction, redirection


class Gateway:
    __gateway_name__ = ''
    config = dict()
    testing = False

    def __init__(self, config):
        self.config = config

    def get_redirection(self, transaction: Transaction) -> redirection.Redirection:  # pragma: nocover
        raise NotImplementedError

    def request_transaction(self, transaction: Transaction) -> Transaction:  # pragma: nocover
        raise NotImplementedError

    def validate_transaction(self, data: dict) -> Transaction:  # pragma: nocover
        raise NotImplementedError

    def verify_transaction(self, transaction: Transaction, data):  # pragma: nocover
        raise NotImplementedError
