import requests


class IpfsApi:
    endpoint = "https://ipfs.io/ipfs/"

    def get_reference(self, path):
        resp = requests.get(f"{self.endpoint}{path}", timeout=600)

        return resp.json()
