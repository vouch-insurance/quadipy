from __future__ import annotations

from typing import Any, Optional, Tuple, Type, Union

from pydantic import BaseModel, validator
from rdflib import BNode, Literal, URIRef


class Quad(BaseModel):
    """Base RDF Fact class.

    Each RDF fact is modeled as subject predicate object with an optional 4th term to specify the named graph.
    This is sometimes referred to as SPOG.

    Attributes:
        subject: Must be a blank node or uri
        predicate: Must be a uri
        obj: We use obj to not use the built-in object keyword in python. Must be a blank node, uri, or literal
        graph: An optional argument that can be used to specify the named graph the fact will belong to. Must be an uri
    """

    subject: Union[BNode, URIRef]
    predicate: URIRef
    obj: Union[URIRef, Literal]
    graph: Optional[URIRef]

    class Config:
        """Pydantic config class"""

        arbitrary_types_allowed = True

    @validator("subject")
    @classmethod
    def _validate_subject(cls, subject: Any) -> Union[BNode, URIRef]:
        return cls._validate_value_type(subject, (BNode, URIRef))  # type: ignore

    @validator("predicate")
    @classmethod
    def _validate_predicate(cls, predicate: Any) -> URIRef:
        return cls._validate_value_type(predicate, (URIRef,))  # type: ignore

    @validator("obj")
    @classmethod
    def _validate_obj(cls, obj: Any) -> Union[URIRef, Literal]:
        return cls._validate_value_type(obj, (URIRef, Literal))  # type: ignore

    @validator("graph")
    @classmethod
    def _validate_graph(cls, graph: Any) -> Any:
        if graph:
            return cls._validate_value_type(graph, (BNode, URIRef, Literal))
        return None

    @classmethod
    def from_tuple(cls, tup: Tuple) -> Quad:
        if len(tup) == 4:
            subject, predicate, obj, graph = tup
            return cls(subject=subject, predicate=predicate, obj=obj, graph=graph)
        if len(tup) == 3:
            subject, predicate, obj = tup
            return cls(subject=subject, predicate=predicate, obj=obj)
        raise ValueError(f"tuple must be of size 3,4 to be quadified: {tup}")

    def to_tuple(self) -> Tuple:
        """Converts quad to a tuple. This method is useful for adding Quad to rdflib Graphs"""
        if self.graph:
            return (self.subject, self.predicate, self.obj, self.graph)
        return (self.subject, self.predicate, self.obj)

    @staticmethod
    def _validate_value_type(value: Any, types: Tuple[Type, ...]) -> Any:
        """Validates the value are the correct data type

        This is used to validate that subject, predicate, objects, and named graph types are the
        correct data type

        Args:
            value: the value to validate

        Returns:
            the value that was validated if it is the correct datatype

        Raises:
            TypeError: If the value isn't the correct datatype
        """
        if isinstance(value, types):
            return value
        raise TypeError(f"subject must be of type {types} and not {type(value)}")
