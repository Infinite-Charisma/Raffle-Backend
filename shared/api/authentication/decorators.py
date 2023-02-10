from time import time
import os
from typing import Optional
from flask import request, abort, g
from functools import wraps
import inspect
from shared.api.authentication.api_key_storage import ApiKeyStorage
from shared.api.authentication.signed_user_handler import (
    SignedUser, SignedUserHandler, SignedUserError, SignedUserRequest, SignedUserSessionHandler, SignedUserSession
)
from shared.api.dependencies import get_dependency


def get_expected_key():
    return os.environ.get("SECRET_KEY", None)


def expect_specific_header_key(key):
    def _expect_header_key(f):
        if inspect.iscoroutinefunction(f):
            @wraps(f)
            async def decorator_async(*args, **kwargs):
                header_key = request.headers.get("x-secret-key")
                if key == header_key:
                    return await f(*args, **kwargs)
                abort(403)
            return decorator_async

        @wraps(f)
        def decorator(*args, **kwargs):
            header_key = request.headers.get("x-secret-key")
            if key == header_key:
                return f(*args, **kwargs)
            abort(403)
        return decorator
    return _expect_header_key


def expect_header_key(f):
    if inspect.iscoroutinefunction(f):
        @wraps(f)
        async def decorator_async(*args, **kwargs):
            header_key = request.headers.get("x-secret-key")
            environ_key = get_expected_key()
            if environ_key and environ_key == header_key:
                return await f(*args, **kwargs)
            abort(403)
        return decorator_async

    @wraps(f)
    def decorator(*args, **kwargs):
        header_key = request.headers.get("x-secret-key")
        environ_key = get_expected_key()
        if environ_key and environ_key == header_key:
            return f(*args, **kwargs)
        abort(403)
    return decorator


def expect_api_key(endpoint, resource_resolver: lambda *args, **kwargs: None):
    def _expect_api_key(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            key = request.headers.get("x-api-key")
            api_key_storage = get_dependency(ApiKeyStorage)
            claims = api_key_storage.get_key_claims(key)
            resource = resource_resolver(*args, **kwargs)
            if any(
                    claim.endpoint == endpoint and (resource is None or resource in claim.resources)
                    for claim in claims):
                return f(*args, **kwargs)
            abort(403)
        return decorator
    return _expect_api_key


def with_signed_user(require_user=False, allow_patch=False):
    def _with_signed_user(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            user_session_handler = SignedUserSessionHandler()

            def _get_headers():
                message = request.headers.get("x-signed-message")
                public_key = request.headers.get("x-public-key")
                account_id = request.headers.get("x-account-id")
                timestamp = request.headers.get("x-signed-timestamp")
                signature = request.headers.get("x-user-signature")
                if all([message, public_key, account_id, timestamp, signature]) and timestamp.isdigit():
                    return SignedUserRequest(message, public_key, account_id, int(timestamp), signature)

                combined = request.headers.get("x-signed-user")
                if allow_patch and hasattr(g, "auth_patch"):
                    combined = g.auth_patch
                if not combined:
                    return None
                splt = combined.split("|")
                if len(splt) < 5:
                    return None
                if len(splt) == 5:
                    message, timestamp, public_key, account_id, signature = splt
                    if all([message, public_key, account_id, timestamp, signature]) and timestamp.isdigit():
                        return SignedUserRequest(message, public_key, account_id, int(timestamp), signature)
                if len(splt) == 6:
                    message, timestamp, public_key, account_id, signature, actual_message = splt
                    if all([message, public_key, account_id, timestamp, signature]) and timestamp.isdigit():
                        return SignedUserRequest(message, public_key, account_id, int(timestamp), signature, actual_message or None)
                return None

            def _get_session_user(user_request: Optional[SignedUserRequest]):
                if not user_request:
                    return None
                session_user = user_session_handler.get()
                if session_user is None:
                    return None
                return session_user.to_signed_user(user_request.message)

            user_request = _get_headers()

            signed_user = None
            user = None
            if user_request and user_request.signature != "x":
                handler = get_dependency(SignedUserHandler)
                try:
                    signed_user = handler.get_signed_user(user_request)
                except SignedUserError:
                    abort(400)

            if signed_user is None:
                session_user = _get_session_user(user_request)

                if session_user is None and require_user:
                    abort(401)  # TODO: use API Exceptions

                if session_user is not None:
                    user = session_user
            else:
                user_session_handler.set(SignedUserSession(
                    account_id=signed_user.account_id,
                    public_key=user_request.public_key,
                    timestamp=int(time())
                ))
                user = signed_user

            g.signed_user = user

            return f(*args, **kwargs)
        return decorator
    return _with_signed_user
