import json
from typing import Any, Callable, Union


# Taken from the structlog implementation
def _json_fallback_handler(obj: Any) -> Any:
    """
    Serialize custom datatypes and pass the rest to __structlog__ & repr().
    """
    # circular imports :(
    from structlog.threadlocal import _ThreadLocalDictWrapper

    if isinstance(obj, _ThreadLocalDictWrapper):
        return obj._dict
    else:
        try:
            return obj.__structlog__()
        except AttributeError:
            return repr(obj)


class CloudJsonRenderer:
    def __init__(
        self,
        serializer: Callable[..., Union[str, bytes]] = json.dumps,
        **dumps_kw: Any,
    ) -> None:
        dumps_kw.setdefault("default", _json_fallback_handler)
        self._dumps_kw = dumps_kw
        self._dumps = serializer

    def __call__(
        self, logger, name: str, event_dict
    ) -> Union[str, bytes]:
        event_dict["severity"] = event_dict["level"]    # Remap level for GCP cloud log processor
        event_dict["message"] = event_dict["event"]     # Remap event for GCP cloud log processor
        return self._dumps(event_dict, **self._dumps_kw)
