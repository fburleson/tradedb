from functools import cached_property


def _get_prop_name(prop: property | cached_property) -> str:
    if isinstance(prop, cached_property):
        return prop.func.__name__
    return prop.fget.__name__  # type: ignore


def create_repr(obj: object, *params: property | cached_property) -> str:
    cls_name = type(obj).__name__
    obj_properties: tuple = tuple(
        f"{_get_prop_name(prop)}={prop.__get__(obj, type(obj))}" for prop in params
    )
    return f"{cls_name}({', '.join(obj_properties)})"
