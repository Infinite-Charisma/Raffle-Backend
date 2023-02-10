from dataclasses import fields, is_dataclass
from typing import Any, Type, TypeVar, get_origin, get_args, Union


T = TypeVar('T')


def parse(cls: Type[T], d: dict[str, Any]) -> T:
    assert is_dataclass(cls)

    def _split_optional(field: Type):
        args = get_args(field)
        is_optional = get_origin(field) is Union and type(None) in args and len(args) == 2
        if not is_optional:
            return False, field
        return True, next(arg for arg in args if arg != type(None))     # noqa: E721

    cls_fields = {}

    for field in fields(cls):
        is_optional, field_type = _split_optional(field.type)
        value = d.get(field.name)
        if value is None and not is_optional:
            raise KeyError(f"Field {field.name} should not be None")
        if value is None and is_optional:
            cls_fields[field.name] = None
            continue
        if get_origin(field_type) == list:
            args = get_args(field_type)
            if len(args) == 0:
                cls_fields[field.name] = value
            else:
                arg = args[0]
                if is_dataclass(arg):
                    cls_fields[field.name] = [parse(arg, item) for item in value]
                else:
                    cls_fields[field.name] = [arg(item) for item in value]
            continue
        if is_dataclass(field_type):
            cls_fields[field.name] = parse(field_type, value)
            continue
        cls_fields[field.name] = field_type(value)

    return cls(**cls_fields)
