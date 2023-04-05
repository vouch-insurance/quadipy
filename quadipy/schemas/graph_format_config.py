import json
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Extra, validator
from rdflib import Literal, Namespace, URIRef

from quadipy.schemas import format_namespace
from quadipy.schemas.predicate_mapping import PredicateMapping
from quadipy.schemas.quad import Quad


class GraphFormatConfig(BaseModel):
    """Graph formatting configuration class

    This class stores configuration of how to convert tabular data into RDF graph data.
    Some examples of sample configurations can be found in the `examples/` directory.

    Attributes:
        source_name: A string that is used to describe the source (i.e. "wikipedia" for data from wikipedia)
        predicate_mapping: A dictionary that maps the column_name to a predicate in URI form
        primary_key: The primary key of the row (usually something like `id`) that will the subject of every quad
        subject_namespace: A string prepended to the quad's subject as a namespace, instead of just using the value of the `primary_key`.
        graph_namespace: Similar to `subject_namespace` in that this will assign each fact to a named graph with the `graph_namespace`.
        date_field: The column in your dataset that the fact's "date" will be pulled from. When specified, the named graph field in each fact will be build from the date.
    """

    source_name: str
    predicate_mapping: Dict[str, PredicateMapping]
    primary_key: str
    subject_namespace: Optional[Namespace]
    graph_namespace: Optional[Namespace]
    date_field: Optional[str]

    class Config:
        """Pydantic config class"""

        arbitrary_types_allowed = True
        allow_mutation = False
        extra = Extra.allow

    @validator("subject_namespace")
    @classmethod
    def _validate_subject_namespace(cls, value: Optional[str]) -> Optional[Namespace]:
        return format_namespace(value)

    @validator("graph_namespace")
    @classmethod
    def _validate_graph_namespace(cls, value: Optional[str]) -> Optional[Namespace]:
        return format_namespace(value)

    def subject(self, record: Dict) -> URIRef:
        """Creates URI out of primary key of the record

        Args:
            record: A dictonary that contains the data. Must contain the `primary_key` specified in the class

        Returns:
            An rdflib.URIRef with the value of the primary_key value in the record

        Raises:
            AssertionError: The `record` provided lacked the `primary_key` field
        """
        assert (
            self.primary_key in record
        ), f"{self.primary_key} isn't defined in {record}! Each record must have a defined primary key"
        primary_key = str(record[self.primary_key])
        if self.subject_namespace:
            return self.subject_namespace[primary_key]
        return URIRef(primary_key)

    def obj(self, record: Dict, col_name: str) -> Optional[Union[Literal, URIRef]]:
        value = record.get(col_name)
        if value is not None:
            predicate_mapping = self.predicate_mapping[col_name]
            obj_value = predicate_mapping.obj_datatype.value(value)
            return self.add_namespace_to_obj(col_name, obj_value)
        return None

    def add_namespace_to_obj(
        self, col_name: str, obj_value: Union[Literal, URIRef]
    ) -> Union[Literal, URIRef]:
        predicate_mapping = self.predicate_mapping[col_name]
        if predicate_mapping.obj_namespace:
            return predicate_mapping.obj_namespace[obj_value]
        return obj_value

    def named_graph(self, record: Dict) -> Optional[URIRef]:
        if self.date_field:
            graph = self.build_graph_from_date(record)
            return URIRef(graph.strip("/"))
        if self.graph_namespace:
            graph = URIRef(self.graph_namespace)
            return URIRef(graph.strip("/"))
        return None

    def _validate_record_has_date_field(self, record: Dict) -> None:
        assert (
            self.date_field in record
        ), f"{self.date_field} must be defined in {record} in order to build record from date"

    def validate_date_field_is_valid_format(self, record: Dict) -> str:
        self._validate_record_has_date_field(record)
        date_value = record[self.date_field]
        try:
            if isinstance(date_value, date):
                dt = date_value
            else:
                dt = datetime.fromisoformat(date_value)
            return dt.strftime("%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(f"{date_value} isn't a valid date!") from exc

    def build_graph_from_date(self, record: Dict) -> URIRef:
        """Builds named graph URI from a date field in the record

        If you have a field like `created_at` or `updated_at` and want to store that metadata in the named graph
        field, this method will build the named graph URI from the `date_field`

        Examples:
            record = {"created_at": "2022-01-01"} -> URIRef("2022-01-01")

            If the config has a `graph_namespace` defined this would change to
            self.graph_namespace = "graph://wikipedia.org/"

            record = {"created_at": "2022-01-01"} -> URIRef("graph://wikipedia.org/2022-01-01")

        Args:
            record: A dictonary that contains the data

        Returns:
            a rdflib.URIRef of the named graph built from the `date_field`

        Raises:
            ParserError: If the value in the `date_field` isn't a valid date
            AssertionError: If the `record` provided doesn't have the `date_field` defined
        """
        date_value = self.validate_date_field_is_valid_format(record)
        if self.graph_namespace:
            return self.graph_namespace[date_value]
        return URIRef(date_value)

    def map_predicate_mapping_to_quad(
        self, col_name: str, predicate: URIRef, record: Dict
    ) -> Optional[Quad]:
        obj = self.obj(record, col_name)
        if not obj:
            return None
        subject = self.subject(record)
        graph = self.named_graph(record)
        return Quad.from_tuple((subject, predicate, obj, graph))

    def process_quad_list(
        self, value: str, predicate_uri: URIRef, record: Dict
    ) -> List[Quad]:
        quads = []
        subject = self.subject(record)
        graph = self.named_graph(record)
        try:
            val_list = json.loads(value)
            for item in val_list:
                quad = Quad.from_tuple((subject, predicate_uri, Literal(item), graph))
                quads.append(quad)
        except SyntaxError:
            logging.info(f"Can't load list with value: {value}")
        except json.decoder.JSONDecodeError:
            quad = Quad.from_tuple((subject, predicate_uri, Literal(value), graph))
            quads.append(quad)
        return quads

    def quadify(self, record: Dict) -> List[Quad]:
        """Takes a record and translates into a list of Quads

        This process is explained more in-depth in the README but this is the high level method that translates
        a record into a list of Quads that can be inserted in an RDF graph

        Args:
            record: A dictionary that contains the data to be quadified

        Returns:
            A list of Quads
        """
        quads = []
        for col_name, predicate in self.predicate_mapping.items():
            value = record.get(col_name)
            if isinstance(value, str) and value and value[0] == "[":
                quads.extend(
                    self.process_quad_list(value, predicate.predicate_uri, record)
                )
            else:
                quad = self.map_predicate_mapping_to_quad(
                    col_name, predicate.predicate_uri, record
                )
                if quad:
                    quads.append(quad)
        return quads
