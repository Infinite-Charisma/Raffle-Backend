class UnauthorizedException(Exception):
    def __init__(self, reason):
        self._reason = reason
        super().__init__(f"UnauthorizedException: {reason}")

    @property
    def reason(self):
        return self._reason


class ForbiddenException(Exception):
    def __init__(self, reason):
        self._reason = reason
        super().__init__(f"ForbiddenException: {reason}")

    @property
    def reason(self):
        return self._reason
