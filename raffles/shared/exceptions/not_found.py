class NotFoundException(Exception):
    def __init__(self, reason):
        self._reason = reason
        super().__init__(f"NotFoundException: {reason}")

    @property
    def reason(self):
        return self._reason
