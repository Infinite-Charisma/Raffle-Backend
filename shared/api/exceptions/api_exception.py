class ApiException(Exception):
    def __init__(self, code: int, reason: str):
        super().__init__(f"ApiException: {code} - {reason}")
        self._code = code
        self._reason = reason

    @property
    def code(self):
        return self._code

    @property
    def reason(self):
        return self._reason


class BadRequestException(ApiException):
    def __init__(self, reason: str):
        super().__init__(400, f"Bad Request: {reason}")


class UnauthorizedException(ApiException):
    def __init__(self, reason: str):
        super().__init__(401, f"Unauthorized: {reason}")


class PaymentRequiredException(ApiException):
    def __init__(self, reason: str):
        super().__init__(402, f"Payment Required: {reason}")


class ForbiddenException(ApiException):
    def __init__(self, reason: str):
        super().__init__(403, f"Forbidden: {reason}")


class NotFoundException(ApiException):
    def __init__(self, reason: str):
        super().__init__(404, f"Not Found: {reason}")
