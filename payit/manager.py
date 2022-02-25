from typing import Type
from payit import Transaction, Gateway, redirection


class GatewayManager:
    _config = dict()
    _gateways = dict()

    def register(self, gateway_alias, gateway: Type[Gateway]):
        self._gateways[gateway_alias] = gateway
        return self

    def configure(self, config):
        for gateway_alias, gateway_config in config.items():
            if gateway_alias not in self._gateways:
                raise ValueError("Gateway %s not registered." % gateway_alias)

            self._gateways[gateway_alias] = self._gateways[gateway_alias](
                config=gateway_config
            )

        return self

    def get_gateway(self, gateway_alias) -> Gateway:
        return self._gateways[gateway_alias]

    def get_redirection(
        self,
        gateway_alias: str,
        transaction: Transaction,
    ) -> redirection.Redirection:
        return self.get_gateway(gateway_alias).get_redirection(transaction)

    def request(
        self,
        gateway_alias: str,
        transaction: Transaction,
    ) -> Transaction:
        return self.get_gateway(gateway_alias).request_transaction(transaction)

    def validate(self, gateway_alias: str, data: dict) -> Transaction:
        return self.get_gateway(gateway_alias).validate_transaction(data)

    def verify(self, gateway_alias: str, transaction: Transaction, data: dict):
        return self.get_gateway(gateway_alias).verify_transaction(
            transaction, data
        )


class GatewayManagerTesting(GatewayManager):
    def configure(self, config):
        super().configure(config)
        for _, gateway in self._gateways.items():
            gateway.testing = True
