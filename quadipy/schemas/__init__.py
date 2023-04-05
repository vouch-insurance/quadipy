from typing import Optional

from rdflib import Namespace


def format_namespace(namespace: Optional[str]) -> Optional[Namespace]:
    if namespace:
        if not namespace.endswith("/"):
            namespace += "/"
        return Namespace(namespace)
    return None
