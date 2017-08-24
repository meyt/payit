

class PymentException(Exception):
    pass


class GatewayException(PymentException):
    pass


class GatewayNetworkError(GatewayException):
    pass


class GatewayInvalidError(GatewayException):
    pass


class TransactionError(PymentException):
    pass


class TransactionNotFoundError(TransactionError):
    pass


class TransactionInvalidError(TransactionError):
    pass


class TransactionAlreadyPaidError(TransactionError):
    pass
