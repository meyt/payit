from . import Transaction


class Gateway:
    __gateway_name__ = ''
    config = dict()
    testing = False

    def __init__(self, config):
        self.config = config

    def request_transaction(self, transaction: Transaction) -> Transaction:
        pass

    def validate_transaction(self, data: dict) -> Transaction:
        pass

    def verify_transaction(self, transaction: Transaction, data):
        pass
