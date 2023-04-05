import pytest
from pydantic import ValidationError
from rdflib import Namespace, URIRef

from quadipy.schemas.predicate_mapping import ObjectDataTypes, PredicateMapping


def test_serialize():
    mapping = PredicateMapping(predicate_uri="https://schema.org/name")
    assert mapping.predicate_uri == URIRef("https://schema.org/name")
    assert mapping.obj_datatype == ObjectDataTypes.literal
    assert not mapping.obj_namespace


def test_invalid_predicate_uri():
    with pytest.raises(ValidationError):
        PredicateMapping(predicate_uri="https://schema.org/url website")


def test_serialize_custom_datatype():
    mapping = PredicateMapping(
        predicate_uri="https://schema.org/name", obj_datatype="uri"
    )
    assert mapping.obj_datatype == ObjectDataTypes.uri


def test_unsupported_datatype():
    with pytest.raises(ValidationError):
        PredicateMapping(
            predicate_uri="https://schema.org/name", obj_datatype="unsupported_datatype"
        )


def test_obj_namespace():
    mapping = PredicateMapping(
        predicate_uri="https://schema.org/name", obj_namespace="wikipedia/"
    )
    assert mapping.obj_namespace == Namespace("wikipedia/")
