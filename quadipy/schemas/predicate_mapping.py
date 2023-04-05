from __future__ import annotations

from enum import Enum
from functools import partial
from typing import Any, Generator, Optional

from pydantic import BaseModel, validator
from rdflib import XSD, Literal, Namespace, URIRef
from rdflib.term import _is_valid_uri

from quadipy.schemas import format_namespace


class ObjectDataTypes(Enum):
    uri = URIRef
    literal = Literal
    date = partial(Literal, datatype=XSD.date)

    @classmethod
    def __get_validators__(cls) -> Generator:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "ObjectDataTypes":
        try:
            return cls[value]
        except KeyError:
            return cls(value)


class PredicateMapping(BaseModel):
    predicate_uri: URIRef
    obj_datatype: ObjectDataTypes = ObjectDataTypes.literal
    obj_namespace: Optional[Namespace]
    """Class to define relationship between data and predicate

    predicate_uri: The URI the data will be mapped to
    obj_datatype: Datatype that the object will be serialized to defaults to literal but can be one of (literal, date, uri)
    obj_namespace: If the object value should be mapped to a specific namespace
    """

    class Config:
        """Pydantic config class"""

        arbitrary_types_allowed = True
        allow_mutation = False

    @validator("predicate_uri")
    @classmethod
    def _predicate_mapping_serialized_as_uri(cls, predicate_uri: Any) -> URIRef:
        assert _is_valid_uri(predicate_uri), f"{predicate_uri} is not a valid uri"
        return URIRef(predicate_uri)

    @validator("obj_namespace")
    @classmethod
    def _validate_obj_namespace(cls, value: Optional[str]) -> Optional[Namespace]:
        return format_namespace(value)
