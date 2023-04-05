This tutorial will walk you through how to process tabular data and add them to an [`rdflib`](https://github.com/RDFLib/rdflib/) graph

## Installation

```bash
pip install rdflib quadipy
```

## Running quadipy
Using the same config from earlier

```json
{
    "primary_key": "id",
    "source_name": "star wars",
    "predicate_mapping": {
        "height": {
            "predicate_uri": "https://schema.org/height"
        },
        "name": {
            "predicate_uri": "https://schema.org/name"
        },
        "birth_year": {
            "predicate_uri": "https://schema.org/birthDate"
        },
        "gender": {
            "predicate_uri": "https://schema.org/gender"
        }
    }
}
```
Copy this json blob to a file named `example.json`

```python
from quadipy import GraphFormatConfig
from rdflib import Graph

record = {
    "id": 1,
	"name": "Luke Skywalker",
	"height": "172",
	"mass": "77",
	"hair_color": "blond",
	"skin_color": "fair",
	"eye_color": "blue",
	"birth_year": "19BBY",
	"gender": "male",
	"homeworld": "https://swapi.dev/api/planets/1/",
	"films": [
		"https://swapi.dev/api/films/2/",
		"https://swapi.dev/api/films/6/",
		"https://swapi.dev/api/films/3/",
		"https://swapi.dev/api/films/1/",
		"https://swapi.dev/api/films/7/"
	],
	"species": [
		"https://swapi.dev/api/species/1/"
	],
	"vehicles": [
		"https://swapi.dev/api/vehicles/14/",
		"https://swapi.dev/api/vehicles/30/"
	],
	"starships": [
		"https://swapi.dev/api/starships/12/",
		"https://swapi.dev/api/starships/22/"
	],
	"created": "2014-12-09T13:50:51.644000Z",
	"edited": "2014-12-20T21:17:56.891000Z",
	"url": "https://swapi.dev/api/people/1/"
}

config = GraphFormatConfig.parse_file("example.json")
graph = Graph()

quads = config.quadify(record)
for quad in quads:
    graph.add(quad.to_tuple())

print(graph.serialize())

```


Copy this code into a file named `main.py`

Run the code by running:

```bash
python main.py
```

And output should be in `turtle` serialized graph

```
@prefix ns1: <https://schema.org/> .

<1> ns1:birthDate "19BBY" ;
    ns1:gender "male" ;
    ns1:height "172" ;
    ns1:name "Luke Skywalker" .
```
