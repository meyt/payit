

class Redirection:
    url = None
    method = None
    query_params = None
    body_params = None
    header_params = None

    def __init__(self,
                 url: str,
                 method: str,
                 query_params: dict=None,
                 body_params: dict=None,
                 header_params: dict=None):
        for key, value in locals().items():
            setattr(self, key, value)

    def to_dict(self) -> dict:
        return dict(
            url=self.url,
            method=self.method,
            query_params=self.query_params,
            body_params=self.body_params,
            header_params=self.header_params
        )
