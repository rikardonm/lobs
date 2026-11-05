from pathlib import Path
import re
import typing as t


class Templater:
    def __init__(self, bookend: str = "@", overwrite: bool = True, check_all_replaced: bool = True):
        self.bookend = bookend
        self.overwrite = overwrite
        self.check_all_replaced = check_all_replaced

    class TagTransformer(t.Protocol):
        def __call__(self, tag: str, hint: str | None, value: t.Any) -> str:
            ...

    def replace_with_transform(
        self,
        template: Path,
        target: Path,
        values: dict[str, t.Any],
        transform: TagTransformer,
    ):
        new_values: dict[str, str] = {}

        for k, v in values.items():
            ks = k.split(':', maxsplit=1)
            hint = ks[1] if len(ks) > 1 else None
            new_values[k] = transform(k, hint, v)

        self.replace(template, target, new_values)

    def replace(
        self,
        template: Path,
        target: Path,
        values: dict[str, str],
    ):
        """Given a template file, a target and a dictionary of variables, this method
        executes a search for each variable and replaces it with the given value.
        """
        content = template.read_text()
        if wrong_tags := list(k for k in values.keys() if self.bookend in k):
            raise RuntimeError(
                f"Provided keys ({wrong_tags}) for template/target contain bookends! '{template}'/'{target}'"
            )

        for k, v in values.items():
            s_key = f"{self.bookend}{k}{self.bookend}"
            content = content.replace(s_key, v)

        # Ensure the parent node exists
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not self.overwrite:
            raise RuntimeError(f"Overwrite of target '{target}' is disabled.")

        if self.check_all_replaced:
            rx = re.compile(f"{self.bookend}[^{self.bookend}]*{self.bookend}")
            m = rx.findall(content)
            if m:
                raise ValueError(f"Unmatched tags for template {template}: {', '.join(m)}")

        # Dump the contents, directly overwriting what's already there
        target.write_text(content)
