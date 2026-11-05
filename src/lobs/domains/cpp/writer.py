# This module implements a writer object for the C++ language
import typing as t

from lobs import Parameter

_hint_to_type: dict[str, type] = {
    "str": str,
    "int8_t": int,
    "uint8_t": int,
    "int16_t": int,
    "uint16_t": int,
    "int32_t": int,
    "uint32_t": int,
    "bool": bool,
}


def _decay_into_source_by_type(o: t.Any) -> str:
    match o:
        case None:
            return "std::nullopt"
        case True:
            return "true"
        case False:
            return "false"
        case str():
            oo = o.replace('"', '\\"')
            return f'"{oo}"'
        case int():
            return str(o)
        case _:
            raise NotImplementedError(f"Not implemented for object type {type(o)}")


def decay_into_source(o: t.Any, hint: str = "") -> str:
    if isinstance(o, Parameter):
        o = o.value  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

    maybe = _decay_into_source_by_type(o)

    if not hint:
        return maybe

    expected_type = _hint_to_type.get(hint)

    if expected_type is None:
        raise NotImplementedError(f"C++ hint {hint} is not supported!")

    if not isinstance(o, expected_type):
        raise ValueError(
            "Unexpected generated C++ type! "
            f"Want '{expected_type.__name__}' but got '{type(maybe).__name__}' for value {o}"
        )

    return maybe
