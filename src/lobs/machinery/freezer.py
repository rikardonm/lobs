"""Utilities to freeze and unfreeze objects."""
from contextlib import contextmanager
import typing as t


def freeze(obj: object) -> None:
    """Inhibit further modifications to the given object."""

    if hasattr(obj, '__setattr__'):
        old_setter = getattr(obj, '__setattr__', None)
        setattr(obj, '__old_setter__', old_setter)

        def frozen_setattr(self: object, name: t.Any, value: t.Any) -> None:
            raise AttributeError(f"Cannot modify frozen instance of {self.__class__.__name__}")

        obj.__setattr__ = frozen_setattr.__get__(obj, obj.__class__)  # Bind the method to the instance


def is_frozen(obj: object) -> bool:
    """Check if the given object is frozen."""
    return hasattr(obj, '__old_setter__')


def unfreeze(obj: object) -> None:
    """Allow modifications to the given object."""
    if hasattr(obj, '__setattr__') and is_frozen(obj):
        del obj.__setattr__  # Remove the frozen __setattr__ method
        old_setter = getattr(obj, '__old_setter__', None)
        assert old_setter is not None
        obj.__setattr__ = old_setter  # Restore the original __setattr__ method
        delattr(obj, '__old_setter__')  # Clean up the old setter attribute


@contextmanager
def context(obj: object, keep_frozen: bool = False) -> t.Generator[object, None, None]:
    """Context manager to temporarily freeze an object."""
    was_frozen = is_frozen(obj)
    if not was_frozen:
        freeze(obj)
    try:
        yield obj
    finally:
        if keep_frozen:
            return
        if not was_frozen:
            unfreeze(obj)
