from pkg_resources import get_distribution

from quadipy.schemas.graph_format_config import GraphFormatConfig
from quadipy.schemas.predicate_mapping import PredicateMapping
from quadipy.schemas.quad import Quad

__version__ = get_distribution("quadipy").version


__all__ = [
    "Quad",
    "GraphFormatConfig",
    "PredicateMapping",
]
