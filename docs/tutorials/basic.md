This tutorial will show you how to use quadipy step by step

## Install quadipy

```bash
pip intall quadipy
```

## Running quadipy
Given a set of tabular records about planets in the Star Wars universe, we'll create a configuration to transform them into RDF quads.

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
# From https://swapi.dev

config = GraphFormatConfig.parse_file("example.json")
quads = config.quadify(record)

for quad in quads:
    print(quad)
```

Copy this code into a file named `main.py`

Run the code by running:

```bash
>> python main.py
subject=rdflib.term.URIRef('1') predicate=rdflib.term.URIRef('https://schema.org/height') obj=rdflib.term.Literal('172') graph=None
subject=rdflib.term.URIRef('1') predicate=rdflib.term.URIRef('https://schema.org/name') obj=rdflib.term.Literal('Luke Skywalker') graph=None
subject=rdflib.term.URIRef('1') predicate=rdflib.term.URIRef('https://schema.org/birthDate') obj=rdflib.term.Literal('19BBY') graph=None
subject=rdflib.term.URIRef('1') predicate=rdflib.term.URIRef('https://schema.org/gender') obj=rdflib.term.Literal('male') graph=None
```

And now you have created your first quads!

Now it's up to the user to load this RDF data into their DB of choice. In the next tutorial, we show how to serialize the `Quad` into a an RDF DB friendly format
