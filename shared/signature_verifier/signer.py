import ed25519
from .signature_verifier import base58_to_hex


class Signer:
    def sign(self,
             private_key: str,
             message: str):
        assert private_key.startswith("ed25519:")
        privKey = ed25519.SigningKey(
            base58_to_hex(
                private_key[8:].encode("ascii")), encoding="hex")

        signature = privKey.sign(message.encode("ascii"))
        return signature.hex()
