"""
Some (initially private) typing helpers for jsonschema's types.
"""
from typing import Any, Callable, Iterable, Protocol, Tuple, Union

from libs.vendor.referencing import jsonschema

from libs.vendor.jsonschema.protocols import Validator


class SchemaKeywordValidator(Protocol):
    def __call__(
        self,
        validator: Validator,
        value: Any,
        instance: Any,
        schema: referencing_jsonschema.Schema,
    ) -> None:
        ...


id_of = Callable[[referencing_jsonschema.Schema], Union[str, None]]


ApplicableValidators = Callable[
    [referencing_jsonschema.Schema],
    Iterable[Tuple[str, Any]],
]
