import requests
from flask import url_for


class SelfAdminClientUrlResolver:
    def __init__(self, scheme="https"):
        self._scheme = scheme

    def resolve(self, raffle_id):
        return url_for(
            "resolve.resolve", raffle_id=raffle_id,
            _external=True, _scheme=self._scheme)


class AdminApiClient:
    def __init__(self, url_resolver: SelfAdminClientUrlResolver):
        self._url_resolver = url_resolver

    def resolve(self, raffle_id):
        r = requests.post(
            self._url_resolver.resolve(raffle_id),
        )
        return r.json()
