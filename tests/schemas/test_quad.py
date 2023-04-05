import pytest
from pydantic.error_wrappers import ValidationError
from rdflib import Literal, URIRef

from quadipy.schemas.quad import Quad


def test_invalid_datatype():
    tup = ("foo", URIRef("pred"), Literal("bar"))
    with pytest.raises(ValidationError):
        Quad.from_tuple(tup)


def test_from_tuple():
    tup = (URIRef("foo"), URIRef("pred"), Literal("bar"))
    quad = Quad.from_tuple(tup)
    assert quad.subject == tup[0]
    assert quad.predicate == tup[1]
    assert quad.obj == tup[2]
    assert not quad.graph


def test_from_tuple_with_graph():
    tup = (URIRef("foo"), URIRef("pred"), Literal("bar"), URIRef("graph"))
    quad = Quad.from_tuple(tup)
    assert quad.subject == tup[0]
    assert quad.predicate == tup[1]
    assert quad.obj == tup[2]
    assert quad.graph == tup[3]


def test_from_tuple_graph_element_none():
    tup = (URIRef("foo"), URIRef("pred"), Literal("bar"), None)
    quad = Quad.from_tuple(tup)
    assert quad.subject == tup[0]
    assert quad.predicate == tup[1]
    assert quad.obj == tup[2]
    assert not quad.graph


def test_from_tuple_error():
    tup = (URIRef("foo"), URIRef("bar"))
    with pytest.raises(ValueError):
        Quad.from_tuple(tup)


def test_to_tuple_with_graph():
    tup = (URIRef("foo"), URIRef("pred"), Literal("bar"), URIRef("graph"))
    quad = Quad.from_tuple(tup)
    assert quad.to_tuple() == tup
    assert len(quad.to_tuple()) == 4


def test_to_tuple_without_graph():
    tup = (URIRef("foo"), URIRef("pred"), Literal("bar"))
    quad = Quad.from_tuple(tup)
    assert quad.to_tuple() == tup
    assert len(quad.to_tuple()) == 3
