from typing import Optional
from flask import g, session
from dataclasses import dataclass
from shared.dependencies import Dependencies
from shared.signature_verifier import SignatureVerifier
import time
from .api_key_storage import ApiKeyStorage
from hashlib import sha256


def register_signed_user_dependencies(dependencies: Dependencies):
    return dependencies\
        .add_resolver_singleton(ApiKeyStorage.resolver())\
        .add_direct(SignatureVerifier)\
        .add_direct(SignedUserHandler)\



@dataclass
class SignedUser:
    account_id: str
    message: str
    timestamp: int


@dataclass
class SignedUserRequest:
    message: str
    public_key: str
    account_id: str
    timestamp: int
    signature: str
    msg_before_hash: Optional[str] = None


class SignedUserError(Exception):
    pass


class SignedUserHandler:
    timestamp_late_arrival_threshold = 1000 * 60 * 60  # 1 hour

    def __init__(self, signature_verifier: SignatureVerifier):
        self._signature_verifier = signature_verifier

    @property
    def _now(self):
        return int(time.time() * 1000)

    def get_signed_user(self, user_request: SignedUserRequest) -> SignedUser:
        if user_request.msg_before_hash:
            if f"{user_request.message}:{user_request.timestamp}" not in user_request.msg_before_hash:
                raise SignedUserError("Invalid signed message")

            m = sha256()
            m.update(user_request.msg_before_hash.encode("ascii"))
            msg_hash = m.digest()

            if not self._signature_verifier.verify(
                account_id=user_request.account_id,
                public_key=user_request.public_key,
                message=msg_hash,
                signature=user_request.signature
            ):
                raise SignedUserError("Invalid signature")
        else:
            if not self._signature_verifier.verify(
                account_id=user_request.account_id,
                public_key=user_request.public_key,
                message=f"{user_request.message}:{user_request.timestamp}".encode("ascii"),
                signature=user_request.signature
            ):
                raise SignedUserError("Invalid signature")

        if user_request.timestamp < self._now - self.timestamp_late_arrival_threshold:
            raise SignedUserError("Timestamp before late arrival threshold")

        return SignedUser(
            account_id=user_request.account_id,
            message=user_request.message,
            timestamp=user_request.timestamp
        )


def get_signed_user() -> Optional[SignedUser]:
    if not hasattr(g, "signed_user"):
        return None
    return g.signed_user


@dataclass
class SignedUserSession:
    account_id: str
    public_key: str
    timestamp: int

    def to_signed_user(self, message):
        return SignedUser(
            account_id=self.account_id,
            message=message,
            timestamp=int(time.time() * 1000)
        )


class SignedUserSessionHandler:

    def get(self) -> Optional[SignedUserSession]:
        user_session = session.get("auth_user")
        if user_session is None:
            return None
        return SignedUserSession(
            account_id=user_session["account_id"],
            public_key=user_session["public_key"],
            timestamp=user_session["timestamp"]
        )

    def set(self, user_session: SignedUserSession):
        session["auth_user"] = {
            "account_id": user_session.account_id,
            "public_key": user_session.public_key,
            "timestamp": user_session.timestamp,
        }

    def delete(self):
        session["auth_user"] = None
