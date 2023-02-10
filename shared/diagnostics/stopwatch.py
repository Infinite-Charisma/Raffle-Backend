from time import time


class Avg:
    def __init__(self):
        self._value = None
        self._count = 0

    def add_point(self, v: float):
        if self._count == 0:
            self._value = v
        else:
            self._value = (self._value * self._count + v) / (self._count + 1)
        self._count += 1

    @property
    def value(self) -> float:
        return self._value or 0

    @property
    def count(self) -> int:
        return self._count


class MeasurementKey:
    def __init__(self, parents: tuple[str, ...], key: str):
        self._parents = parents
        self._key = key

    @property
    def sig(self):
        return ','.join([*self._parents, self._key])


class Measurement:
    def __init__(self, key: MeasurementKey):
        self.key = key
        self.avg = Avg()

    def __str__(self) -> str:
        return f"{self.key.sig}\t{round(self.avg.value, 4)}, {self.avg.count}, {round(self.avg.value * self.avg.count, 4)}"     # noqa: E501


class Stopwatch:
    def __init__(self):
        self._measurements: dict[str, Measurement] = {}
        self._watches: list[tuple[str, float]] = []

    def start(self, key: str):
        self._watches.append((key, time()))

    def stop(self, key: str):
        while any(self._watches) and self._watches[-1][0] != key:
            self._watches.pop(-1)
        if not any(self._watches):
            return
        _, start = self._watches.pop(-1)

        mes_key = MeasurementKey([key for key, _ in self._watches], key)
        if mes_key.sig not in self._measurements:
            self._measurements[mes_key.sig] = Measurement(mes_key)

        self._measurements[mes_key.sig].avg.add_point(time() - start)

    def reset(self) -> dict[str, float]:
        result = list(self._measurements.values())
        self._measurements = {}
        self._watches = []
        return result
