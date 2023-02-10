from functools import reduce
from time import time
from typing import Any, Callable, Collection, Hashable, Optional, TypeVar
from contextlib import contextmanager

T = TypeVar('T')
TCollection = TypeVar('TCollection')
TKey = TypeVar('TKey')
TValue = TypeVar('TValue')


def group_by(collection: Collection[TCollection],
             key_selection: Callable[[TCollection], TKey],
             value_selector: Callable[[TCollection], TValue] = lambda a: a) -> dict[TKey, list[TValue]]:
    return reduce(lambda d, item: {
        **d, key_selection(item): [
            *d.get(key_selection(item), []),
            value_selector(item)]}, collection, {})


def dedupe_by(items: list[T], key_selector: Callable[[T], Hashable]) -> list[T]:
    lookup = set({})
    deduped_items = []
    for item in items:
        key = key_selector(item)
        if key in lookup:
            continue
        lookup.add(key)
        deduped_items.append(item)
    return deduped_items


def merge_sorted(*colls: list[T], key: Callable[[T], Any] = lambda x: x):
    while any(cols_with_values := [col for col in colls if len(col) > 0]):
        arr = min(cols_with_values, key=lambda t: key(t[0]))
        yield arr[0]
        arr.pop(0)


def avg(_data: list[float]) -> float:
    if (l := len(_data)) == 0:
        return 0
    return sum(_data) / l


def get_closest_value(data: list[T], key: Callable[[T], int], target: int) -> Optional[T]:
    if len(data) == 0:
        return None
    return sorted(
        data,
        key=lambda p: abs(key(p) - target))[0]


@contextmanager
def timeit(op_count=None):
    start = time()
    yield
    dt = time() - start
    print(dt)
    if op_count is not None:
        print("time per op:", dt / op_count)
