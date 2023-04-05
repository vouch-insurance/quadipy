from datetime import date, datetime

import pytest
from rdflib import RDF, XSD, Literal, Namespace, URIRef

from quadipy.schemas.graph_format_config import GraphFormatConfig
from quadipy.schemas.predicate_mapping import ObjectDataTypes, PredicateMapping
from quadipy.schemas.quad import Quad

PREDICATE_MAPPING = {
    "organization_name": {"predicate_uri": "https://schema.org/name"},
    "number_of_lightsabers": {
        "predicate_uri": "https://starwarsdb.og/number_of_lightsabers"
    },
    "url": {"predicate_uri": "https://schema.org/url", "obj_datatype": "uri"},
    "date_created": {
        "predicate_uri": "https://schema.org/dateCreated",
        "obj_datatype": "date",
    },
    "planet": {
        "predicate_uri": "https://starwarsdb.org/planet",
        "obj_datatype": "uri",
        "obj_namespace": "starwars_planet",
    },
    "industry": {"predicate_uri": "https://schema.org/industry"},
}
config = GraphFormatConfig(
    primary_key="id", predicate_mapping=PREDICATE_MAPPING, source_name="star wars"
)


def test_serialize_predicate_mapping_uri():
    assert config.predicate_mapping["url"] == PredicateMapping(
        predicate_uri="https://schema.org/url",
        obj_datatype=ObjectDataTypes.uri,
    )


def test_serialize_predicate_mapping():
    config = GraphFormatConfig(
        primary_key="id",
        predicate_mapping={
            "organization_name": PredicateMapping(
                predicate_uri="https://schema.org/name",
            )
        },
        source_name="star wars",
    )
    assert config.predicate_mapping["organization_name"] == PredicateMapping(
        predicate_uri="https://schema.org/name",
        obj_datatype="literal",
    )


def test_validate_no_subject_namespace():
    assert not config.subject_namespace


def test_validate_subject_namespace():
    new_config = GraphFormatConfig(
        subject_namespace="foo", **config.dict(exclude_none=True)
    )
    assert new_config.subject_namespace == Namespace("foo/")


def test_validate_subject_namespace_trailing_slash():
    new_config = GraphFormatConfig(
        subject_namespace="foo/", **config.dict(exclude_none=True)
    )
    assert new_config.subject_namespace == Namespace("foo/")


def test_validate_subject_namespace_none():
    new_config = GraphFormatConfig(
        subject_namespace=None, **config.dict(exclude_none=True)
    )
    assert not new_config.subject_namespace


def test_subject_no_primary_key():
    record = {"organization_name": "Rebel Alliance"}
    with pytest.raises(AssertionError):
        config.subject(record)


def test_subject():
    record = {"organization_name": "Rebel Alliance", "id": 1}
    subj = config.subject(record)
    assert subj == URIRef("1")


def test_subject_with_namespace():
    record = {"organization_name": "Rebel Alliance", "id": 1}
    config_with_subject_namepspace = GraphFormatConfig(
        subject_namespace="source://", **config.dict(exclude_none=True)
    )
    subj = config_with_subject_namepspace.subject(record)
    assert subj == URIRef("source://1")


def test_obj():
    record = {"organization_name": "Rebel Alliance"}
    value = config.obj(record, "organization_name")
    assert value == Literal("Rebel Alliance")


def test_obj_false_bool():
    record = {"organization_name": False}
    value = config.obj(record, "organization_name")
    assert value == Literal(False)


def test_obj_none():
    record = {"organization_name": None}
    value = config.obj(record, "organization_name")
    assert not value


def test_obj_int():
    record = {"number_of_lightsabers": 10}
    value = config.obj(record, "number_of_lightsabers")
    assert value == Literal(10)


def test_obj_uri():
    record = {"url": "https://swapi.dev/"}
    value = config.obj(record, "url")
    assert value == URIRef("https://swapi.dev/")


def test_obj_date():
    record = {"date_created": "2022-01-01"}
    value = config.obj(record, "date_created")
    assert value == Literal("2022-01-01", datatype=XSD.date)


def test_obj_value_not_exist():
    record = {"number_of_lightsabers": 10}
    value = config.obj(record, "key_that_doesnt_exist")
    assert not value


def test_obj_value_list():
    record = {"number_of_lightsabers": [10, 12, 15]}
    value = config.obj(record, "number_of_lightsabers")
    assert value == Literal([10, 12, 15])


def test_obj_with_namespace():
    record = {"planet": "tatooine"}
    value = config.obj(record, "planet")
    assert value == URIRef("starwars_planet/tatooine")


def test_graph_none():
    record = {"organization_name": "Rebel Alliance"}
    graph = config.named_graph(record)
    assert not graph


def test_graph_from_date():
    record = {"organization_name": "Rebel Alliance", "created_at": "2022-01-01"}
    config_with_graph = GraphFormatConfig(
        date_field="created_at", **config.dict(exclude_none=True)
    )
    graph = config_with_graph.named_graph(record)
    assert graph == URIRef("2022-01-01")


def test_graph_from_date_with_namespace():
    record = {"organization_name": "Rebel Alliance", "created_at": "2022-01-01"}
    config_with_graph = GraphFormatConfig(
        date_field="created_at",
        graph_namespace="star-wars",
        **config.dict(exclude_none=True),
    )
    graph = config_with_graph.named_graph(record)
    assert graph == URIRef("star-wars/2022-01-01")


def test_graph_from_namespace():
    record = {"foo": "bar"}
    config_with_graph = GraphFormatConfig(
        graph_namespace="graph://test", **config.dict(exclude_none=True)
    )
    graph = config_with_graph.named_graph(record)
    assert graph == URIRef("graph://test")


def test_validate_date_format():
    record = {"created_at": "2022-01-01"}
    date_config = GraphFormatConfig(
        date_field="created_at", **config.dict(exclude_none=True)
    )
    assert date_config.validate_date_field_is_valid_format(record) == "2022-01-01"


def test_validate_date_format_date_type():
    today = date.today()
    record = {"created_at": today}
    date_config = GraphFormatConfig(
        date_field="created_at", **config.dict(exclude_none=True)
    )
    assert date_config.validate_date_field_is_valid_format(record) == str(today)


def test_validate_date_format_datetime_type():
    now = datetime.now()
    record = {"created_at": now}
    date_config = GraphFormatConfig(
        date_field="created_at", **config.dict(exclude_none=True)
    )
    assert date_config.validate_date_field_is_valid_format(record) == str(now.date())


def test_validate_date_format_doesnt_have_field():
    record = {"foo": "bar"}
    with pytest.raises(AssertionError):
        config.validate_date_field_is_valid_format(record)


def test_validate_date_format_incorrect_format():
    record = {"created_at": "not_a_date"}
    date_config = GraphFormatConfig(
        date_field="created_at", **config.dict(exclude_none=True)
    )
    with pytest.raises(ValueError):
        date_config.validate_date_field_is_valid_format(record)


def test_build_from_date():
    record = {"created_at": "2022-01-01"}
    config_with_date_field = GraphFormatConfig(
        date_field="created_at", **config.dict(exclude_none=True)
    )
    graph = config_with_date_field.build_graph_from_date(record)
    assert graph == URIRef("2022-01-01")


def test_build_from_date_with_namespace():
    record = {"created_at": "2022-01-01"}
    config_with_graph = GraphFormatConfig(
        date_field="created_at",
        graph_namespace="graph://test",
        **config.dict(exclude_none=True),
    )
    graph = config_with_graph.build_graph_from_date(record)
    assert graph == URIRef("graph://test/2022-01-01")


def test_build_from_datetime_with_namespace():
    now = datetime.now()
    record = {"created_at": now}
    config_with_graph = GraphFormatConfig(
        date_field="created_at",
        graph_namespace="graph://test",
        **config.dict(exclude_none=True),
    )
    graph = config_with_graph.build_graph_from_date(record)
    assert graph == URIRef(f"graph://test/{now.date()}")


def test_map_predicate_to_quad():
    record = {"organization_name": "Rebel Alliance", "id": 1}
    quad = config.map_predicate_mapping_to_quad(
        "organization_name", RDF.predicate, record
    )
    assert quad.subject == config.subject(record)
    assert quad.predicate == RDF.predicate
    assert quad.obj == Literal("Rebel Alliance")
    assert not quad.graph


def test_map_predicate_no_obj():
    record = {"id": 1}
    quad = config.map_predicate_mapping_to_quad("not_a_col", RDF.type, record)
    assert not quad


def test_map_predicate_with_graph():
    record = {"id": 1, "organization_name": "Rebel Alliance"}
    config_with_graph = GraphFormatConfig(
        graph_namespace="star-wars", **config.dict(exclude_none=True)
    )
    predicate = URIRef("https://schema.org/name")
    quad = config_with_graph.map_predicate_mapping_to_quad(
        "organization_name", predicate, record
    )
    assert quad.graph == URIRef("star-wars")


def test_quadify_doesnt_include_none():
    record = {"id": 1, "not_a_label": "value"}
    quads = config.quadify(record)
    assert len(quads) == 0


def test_quadify():
    record = {"id": 1, "organization_name": "Rebel Alliance"}
    quads = config.quadify(record)
    assert len(quads) == 1


def test_list_obj():
    record = {
        "id": 1,
        "industry": '["Biotech", "Diagnostics"]',
    }
    quads = config.quadify(record)
    assert len(quads) == 2


def test_process_quad_list():
    record = {
        "id": 1,
        "industry": '["Biotech", "Diagnostics"]',
    }
    predicate_uri = URIRef("https://schema.org/industry")
    subject = URIRef("1")
    quad_predicate = URIRef("https://schema.org/industry")
    quads = config.process_quad_list(
        '["Biotech", "Diagnostics"]', predicate_uri, record
    )
    assert quads == [
        Quad(subject=subject, predicate=quad_predicate, obj=Literal("Biotech")),
        Quad(subject=subject, predicate=quad_predicate, obj=Literal("Diagnostics")),
    ]


def test_bad_list_process_quad_list():
    record_blank = {"id": 1, "industry": "[Blank] and other strings"}
    record_empty_list = {"id": 2, "industry": "[]"}

    predicate_uri = URIRef("https://schema.org/industry")
    subject = URIRef("1")
    quad_predicate = URIRef("https://schema.org/industry")

    quads_blank = config.process_quad_list(
        "[Blank] and other strings", predicate_uri, record_blank
    )
    assert quads_blank == [
        Quad(
            subject=subject,
            predicate=quad_predicate,
            obj=Literal("[Blank] and other strings"),
        ),
    ]
    quads_empty_list = config.process_quad_list("[]", predicate_uri, record_empty_list)
    assert quads_empty_list == []
