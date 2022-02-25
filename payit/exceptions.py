class PayitException(Exception):
    pass


class GatewayException(PayitException):
    pass


class GatewayNetworkError(GatewayException):
    pass


class GatewayInvalidError(GatewayException):
    pass


class TransactionError(PayitException):
    pass


class TransactionNotFoundError(TransactionError):
    pass


class TransactionInvalidError(TransactionError):
    pass


class TransactionAlreadyPaidError(TransactionError):
    pass
