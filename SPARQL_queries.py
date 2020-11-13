import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON, CSV


def create_df_level1(latitude='49.487777777', longitude='8.466111111', radius='15', limit='30'):
    endpoint = 'https://query.wikidata.org/sparql'
    query = '''
        prefix bd:       <http://www.bigdata.com/rdf#>
        prefix geo:      <http://www.opengis.net/ont/geosparql#>
        prefix wd:       <http://www.wikidata.org/entity/>
        prefix wdt:      <http://www.wikidata.org/prop/direct/>
        prefix wikibase: <http://wikiba.se/ontology#>


        SELECT ?xLabel ?x ?somebodyLabel ?somebody ?classLabel ?otherLocation ?dist
        WHERE
        {{
          BIND('Point({longitude} {latitude})'^^geo:wktLiteral AS ?currentLocation).
          SERVICE wikibase:around {{
              ?x wdt:P625 ?otherLocation. 
              bd:serviceParam wikibase:center ?currentLocation. 
              bd:serviceParam wikibase:radius '{radius}'. 
          }}
          # x is named after
          ?x wdt:P138 ?somebody .

          # which Class is x (e.g. Street, church)
          ?x wdt:P31  ?class . 

          # x is a Street
          #?x wdt:P31 wd:Q79007 .

          # hat Staat Deutschland
          # ?x wdt:P17  ?Q183 .

          # Retrieve Labels
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de". }} 

          # Compute Distance
          # BIND(geof:distance(?otherLocation, ?currentLocation) as ?dist) 
        }} 

        LIMIT {limit}
        #ORDER BY ?dist

        '''.format(longitude=longitude, latitude=latitude, radius=radius, limit=limit)

    # Initializing SPARQL Wrapper and querying
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    df = pd.DataFrame(results['results']['bindings'])
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x['value'])

    return df


def create_map_level1(latitude='49.487777777', longitude='8.466111111', radius='15', limit='30'):
    map = '''https://query.wikidata.org/embed.html#%23defaultView%3AMap%0A%20%20%20%20%20%20%20%20prefix%20bd%3A%20%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.bigdata.com%2Frdf%23%3E%0A%20%20%20%20%20%20%20%20prefix%20geo%3A%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.opengis.net%2Font%2Fgeosparql%23%3E%0A%20%20%20%20%20%20%20%20prefix%20wd%3A%20%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%0A%20%20%20%20%20%20%20%20prefix%20wdt%3A%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0A%20%20%20%20%20%20%20%20prefix%20wikibase%3A%20%3Chttp%3A%2F%2Fwikiba.se%2Fontology%23%3E%0A%0A%0A%20%20%20%20%20%20%20%20SELECT%20%3FxLabel%20%3Fx%20%3FsomebodyLabel%20%3Fsomebody%20%3FclassLabel%20%3FotherLocation%20%3Fdist%0A%20%20%20%20%20%20%20%20WHERE%0A%20%20%20%20%20%20%20%20%7B%0A%20%20%20%20%20%20%20%20%20%20BIND('Point({longitude}%20{latitude})'%5E%5Egeo%3AwktLiteral%20AS%20%3FcurrentLocation).%0A%20%20%20%20%20%20%20%20%20%20SERVICE%20wikibase%3Aaround%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3Fx%20wdt%3AP625%20%3FotherLocation.%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20bd%3AserviceParam%20wikibase%3Acenter%20%3FcurrentLocation.%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20bd%3AserviceParam%20wikibase%3Aradius%20'{radius}'.%20%0A%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%23%20x%20is%20named%20after%0A%20%20%20%20%20%20%20%20%20%20%3Fx%20wdt%3AP138%20%3Fsomebody%20.%0A%0A%20%20%20%20%20%20%20%20%20%20%23%20which%20Class%20is%20x%20(e.g.%20Street%2C%20church)%0A%20%20%20%20%20%20%20%20%20%20%3Fx%20wdt%3AP31%20%20%3Fclass%20.%20%0A%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%23%20x%20is%20a%20Street%0A%20%20%20%20%20%20%20%20%20%20%23%3Fx%20wdt%3AP31%20wd%3AQ79007%20.%0A%0A%20%20%20%20%20%20%20%20%20%20%23%20hat%20Staat%20Deutschland%0A%20%20%20%20%20%20%20%20%20%20%23%20%3Fx%20wdt%3AP17%20%20%3FQ183%20.%0A%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%23%20Retrieve%20Labels%0A%20%20%20%20%20%20%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22de%22.%20%7D%20%0A%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%23%20Compute%20Distance%0A%20%20%20%20%20%20%20%20%20%20%23%20BIND(geof%3Adistance(%3FotherLocation%2C%20%3FcurrentLocation)%20as%20%3Fdist)%20%0A%20%20%20%20%20%20%20%20%7D%20%0A%0A%20%20%20%20%20%20%20%20LIMIT%20{limit}%0A%20%20%20%20%20%20%20%20%23ORDER%20BY%20%3Fdist'''.format(
        longitude=longitude, latitude=latitude, radius=radius, limit=limit)

    return map
