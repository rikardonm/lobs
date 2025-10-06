import typing as t
import dataclasses


@dataclasses.dataclass
class CompilationFlags:
    """This class represents compilation flags for a C++ project.

    Each attribute corresponds to a specific compilation flag. If the attribute is set to True, the flag is enabled.

    The attribute names follow the convention of starting with 'w_' to indicate warning flags.
    This suffix shall be used when adding new flags dynamically,
    and will be replaced with '-W' when generating the actual compiler arguments.
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
        if not key.startswith('w_'):
            raise KeyError(f"Invalid compilation flag '{key}'. Must start with 'w_'.")
        if key not in self.__dataclass_fields__:
            # Create a new field dynamically
            field = dataclasses.Field(
                default=None,
                default_factory=lambda: None,
                init=True,
                repr=True,
                hash=None,
                compare=True,
                metadata={},
                kw_only=False,
            )
            field.name = key
            field.type = bool | None
            self.__dataclass_fields__[key] = field
            setattr(self, key, value)
        else:
            setattr(self, key, value)

    def get_all(self) -> list[dataclasses.Field[t.Any]]:
        # although it would be very nice and clean to use `dataclasses.fields(self)`
        # it does not easily allow us to dynamically add fields to the dataclass
        return list(self.__dataclass_fields__.values())
