from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON, N3
from pprint import pprint

sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
sparql.setQuery('''
SELECT ?street ?streetLabel ?cityLabel ?personLabel ?coordinates
WHERE
{
    ?street wdt:P31 wd:Q79007 .
    ?street wdt:P17 wd:Q183 .
    ?street wdt:P131 ?city .
    ?street wdt:P138 ?person .
    # ?street wdt:Q515 wd:Q64 .
    ?person wdt:P31 wd:Q5 .
    ?street wdt:P625 ?coordinates
    SERVICE wikibase:label { bd:serviceParam wikibase:language "de" }
}
ORDER BY ?city
''')
sparql.setReturnFormat(JSON)
qres = sparql.query().convert()
pprint(qres)

for result in qres['results']['bindings']:
    print(result['personLabel'])

