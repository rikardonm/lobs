import typing as t
import dataclasses


@dataclasses.dataclass
class CompilationFlags:
    """This class represents compilation flags for a C++ project.

    Each attribute corresponds to a specific compilation flag. If the attribute is set to True, the flag is enabled.

    The attribute names follow the convention of starting with 'w_' to indicate warning flags.
    This prefix shall be used when adding new flags dynamically,
    and will be replaced with '-W' when generating the actual compiler arguments.

    Flags that do not have the suffix, will not be modified (other than replacing '_' with '-').
    """
    w_all: bool | None = None
    w_extra: bool | None = None
    w_pedantic: bool | None = None
    w_error: bool | None = None
    w_uninitialized: bool | None = None
    w_no_missing_field_initializers: bool | None = None
    w_no_unused_parameter: bool | None = None
    w_no_unused_variable: bool | None = None
    w_no_unused_function: bool | None = None
    w_no_unused_but_set_variable: bool | None = None
    w_no_sign_compare: bool | None = None
    w_no_unknown_pragmas: bool | None = None
    w_no_attributes: bool | None = None
    w_no_deprecated_declarations: bool | None = None
    w_unused_result: bool | None = None
    w_switch: bool | None = None

    def __getitem__(self, key: str) -> bool | None:
        return getattr(self, key)

    def __setitem__(self, key: str, value: bool | None) -> None:
        setattr(self, key, value)

    @staticmethod
    def _sanitize_key(key: str) -> tuple[str, str]:
        _type, tail = key.split("_", maxsplit=1)
        if not tail:
            raise ValueError(f"Unexpected compile flag format!: {key}")
        if len(_type) != 1:
            raise ValueError(f"Unexpected compile flag type value: {_type}")
        return (_type, tail.replace("_", "-"))

    def get_all(self) -> dict[str, bool | None]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def get_split(self) -> list[tuple[str, str]]:
        return [
            self._sanitize_key(key)
            for key, value in self.get_all().items()
            if value
        ]
