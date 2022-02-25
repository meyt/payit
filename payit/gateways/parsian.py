from zeep import Client, exceptions as zeep_exceptions

from payit import (
    Gateway,
    Transaction,
    Redirection,
    GatewayNetworkError,
    TransactionError,
    TransactionAlreadyPaidError,
)


class ParsianGateway(Gateway):
    """
    Parsian Bank Gateway (PECCO)

    Home: https://pec.ir
    Documentation: https://pgw.pec.ir/IPG/NewIPGDocument.pdf
    """

    __gateway_name__ = "parsian"
    __gateway_unit__ = "IRR"
    __config_params__ = ["pin", "callback_url", "proxies"]
    _server_url_request = (
        "https://pec.shaparak.ir" "/NewIPGServices/Sale/SaleService.asmx?WSDL"
    )
    _server_url_verify = (
        "https://pec.shaparak.ir"
        "/NewIPGServices/Confirm/ConfirmService.asmx?WSDL"
    )

    _response_message_map = {
        "-32768": "UnknownError",
        "-1552": "PaymentRequestIsNotEligibleToReversal",
        "-1551": "PaymentRequestIsAlreadyReversed",
        "-1550": "PaymentRequestStatusIsNotReversible",
        "-1549": "MaxAllowedTimeToReversalHasExceeded",
        "-1548": "BillPaymentRequestServiceFailed",
        "-1540": "InvalidConfirmRequestService",
        "-1536": "TopupChargeServiceTopupChargeRequestFailed",
        "-1533": "PaymentIsAlreadyConfirmed",
        "-1532": "MerchantHasConfirmedPaymentRequest",
        "-1531": "CannotConfirmNonSuccessfulPayment",
        "-1530": "MerchantConfirmPaymentRequestAccessViolated",
        "-1528": "ConfirmPaymentRequestInfoNotFound",
        "-1527": "CallSalePaymentRequestServiceFailed",
        "-1507": "ReversalCompleted",
        "-1505": "PaymentConfirmRequested",
        "-138": "CanceledByUser",
        "-132": "InvalidMinimumPaymentAmount",
        "-131": "InvalidToken",
        "-130": "TokenIsExpired",
        "-128": "InvalidIpAddressFormat",
        "-127": "InvalidMerchantIp",
        "-126": "InvalidMerchantPin",
        "-121": "InvalidStringIsNumeric",
        "-120": "InvalidLength",
        "-119": "InvalidOrganizationId",
        "-118": "ValueIsNotNumeric",
        "-117": "LengthIsLessOfMinimum",
        "-116": "LengthIsMoreOfMaximum",
        "-115": "InvalidPayId",
        "-114": "InvalidBillId",
        "-113": "ValueIsNull",
        "-112": "OrderIdDuplicated",
        "-111": "InvalidMerchantMaxTransAmount",
        "-108": "ReverseIsNotEnabled",
        "-107": "AdviceIsNotEnabled",
        "-106": "ChargeIsNotEnabled",
        "-105": "TopupIsNotEnabled",
        "-104": "BillIsNotEnabled",
        "-103": "SaleIsNotEnabled",
        "-102": "ReverseSuccessful",
        "-101": "MerchantAuthenticationFailed",
        "-100": "MerchantIsNotActive",
        "-1": "Server Error",
        "0": "Successful",
        "1": "Refer To Card Issuer Decline",
        "2": "Refer To Card Issuer Special Conditions",
        "3": "Invalid Merchant",
        "5": "Do Not Honour",
        "6": "Error",
        "8": "Honour With Identification",
        "9": "Request In-progress",
        "10": "Approved For Partial Amount",
        "12": "Invalid Transaction",
        "13": "Invalid Amount",
        "14": "Invalid Card Number",
        "15": "No Such Issuer",
        "17": "Customer Cancellation",
        "20": "Invalid Response",
        "21": "No Action Taken",
        "22": "Suspected Malfunction",
        "30": "Format Error",
        "31": "Bank Not Supported By Switch",
        "32": "Completed Partially",
        "33": "Expired Card Pick Up",
        "38": "Allowable PIN Tries Exceeded Pick Up",
        "39": "No Credit Account",
        "40": "Requested Function is not supported",
        "41": "Lost Card",
        "43": "Stolen Card",
        "45": "Bill Can not Be Payed",
        "51": "No Sufficient Funds",
        "54": "Expired Account",
        "55": "Incorrect PIN",
        "56": "No Card Record",
        "57": "Transaction Not Permitted To CardHolder",
        "58": "Transaction Not Permitted To Terminal",
        "59": "Suspected Fraud-Decline",
        "61": "Exceeds Withdrawal Amount Limit",
        "62": "Restricted Card-Decline",
        "63": "Security Violation",
        "65": "Exceeds Withdrawal Frequency Limit",
        "68": "Response Received Too Late",
        "69": "Allowable Number Of PIN Tries Exceeded",
        "75": "PIN Reties Exceeds-Slm",
        "78": "Deactivated Card-Slm",
        "79": "Invalid Amount-Slm",
        "80": "Transaction Denied-Slm",
        "81": "Cancelled Card-Slm",
        "83": "Host Refuse-Slm",
        "84": "Issuer Down-Slm",
        "91": "Issuer Or Switch Is Inoperative",
        "92": "Not Found for Routing",
        "93": "Cannot Be Completed",
    }

    def get_redirection(self, transaction) -> Redirection:
        return Redirection(
            url="https://pec.shaparak.ir/NewIPG",
            query_params=dict(Token=transaction.id),
            method="get",
        )

    def request_transaction(self, transaction: Transaction) -> Transaction:
        client = Client(self._server_url_request)
        if "proxies" in self.config:
            client.transport.session.proxies = self.config["proxies"]
        try:
            data = {
                "LoginAccount": self.config["pin"],
                "OrderId": transaction.order_id,
                "Amount": int(transaction.amount),
                "CallBackUrl": self.config["callback_url"],
            }
            result = client.service.SalePaymentRequest(requestData=data)
            token = result.Token
            status = int(result.Status)
            if token and status == 0:
                transaction.id = str(token)

            else:
                raise TransactionError(
                    "Parsian: %s-%s"
                    % (status, self._response_message_map[str(status)])
                )

        except zeep_exceptions.Fault:
            raise TransactionError("Parsian: invalid information.")

        except zeep_exceptions.Error:
            raise GatewayNetworkError

        return transaction

    def validate_transaction(self, data: dict) -> Transaction:
        transaction = Transaction()
        transaction.id = data["Token"]
        transaction.meta = data
        if "status" in data and int(data["status"]) == 0:
            transaction.validate_status = True
        return transaction

    def verify_transaction(self, transaction: Transaction, data):
        try:
            data = {
                "LoginAccount": self.config["pin"],
                "Token": transaction.id,
            }
            client = Client(self._server_url_verify)
            if "proxies" in self.config:
                client.transport.session.proxies = self.config["proxies"]

            result = client.service.ConfirmPayment(requestData=data)
            status = int(result.Status)
            if status == -1533:
                raise TransactionAlreadyPaidError(
                    "Parsian: Transaction already paid"
                )

            elif status != 0:
                raise TransactionError(
                    "Parsian: %s-%s"
                    % (status, self._response_message_map[str(status)])
                )

        except zeep_exceptions.Error:
            raise GatewayNetworkError

        transaction.pan = result.CardNumberMasked
        return transaction
