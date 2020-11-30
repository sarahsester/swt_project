import pandas as pd
import numpy as np
import haversine as hs
from SPARQLWrapper import SPARQLWrapper, JSON


def create_df_level1(latitude, longitude, radius, limit):
    query = '''
        prefix bd:       <http://www.bigdata.com/rdf#>
        prefix geo:      <http://www.opengis.net/ont/geosparql#>
        prefix wd:       <http://www.wikidata.org/entity/>
        prefix wdt:      <http://www.wikidata.org/prop/direct/>
        prefix wikibase: <http://wikiba.se/ontology#>


        SELECT ?xLabel ?x ?somebodyLabel ?somebody ?Location 
               (GROUP_CONCAT(?classLabel; separator=', ') AS ?Description)         
        WHERE
        {{
          BIND('Point({longitude} {latitude})'^^geo:wktLiteral AS ?currentLocation).
          SERVICE wikibase:around {{
              ?x wdt:P625 ?Location. 
              bd:serviceParam wikibase:center ?currentLocation. 
              bd:serviceParam wikibase:radius '{radius}'. 
          }}
          # x is named after
          ?x wdt:P138 ?somebody .
          
          # that somebody is a human
          ?somebody wdt:P31 wd:Q5 .

          # which Class is x (e.g. Street, church)
          ?x wdt:P31  ?class . 
          
          # the class has a german label 
          ?class rdfs:label ?classLabel .
          FILTER( lang(?classLabel) = "de" )
          
          # Retrieve Labels
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de". }} 
          
        }} 
        GROUP BY ?xLabel ?x ?somebodyLabel ?somebody ?Location
        LIMIT {limit}
        '''.format(longitude=longitude, latitude=latitude, radius=radius, limit=limit)

    # Initializing SPARQL Wrapper and querying
    endpoint = 'https://query.wikidata.org/sparql'
    sparql = SPARQLWrapper(endpoint, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    df = pd.DataFrame(results['results']['bindings'])
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x['value'])

    # Compute distance and sort according to distance
    df['Distance (km)'] = df['Location'].apply(lambda point: compute_distance(new_point=point,
                                                                              current_longitude=longitude,
                                                                              current_latitude=latitude))
    # Sort according to distance
    df.sort_values(by=['Distance (km)'], inplace=True)

    # Rename columns
    df.rename(columns={"xLabel": "Object", "somebodyLabel": "Person", "somebody": "Further Results",
                       "Location": "Object Location"}, inplace=True)

    return df


def create_map_level1(latitude, longitude, radius, limit):
    map_ = '''https://query.wikidata.org/embed.html#%23defaultView%3AMap%0A%20%20%20%20%20%20%20%20prefix%20bd%3A%20%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.bigdata.com%2Frdf%23%3E%0A%20%20%20%20%20%20%20%20prefix%20geo%3A%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.opengis.net%2Font%2Fgeosparql%23%3E%0A%20%20%20%20%20%20%20%20prefix%20wd%3A%20%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%0A%20%20%20%20%20%20%20%20prefix%20wdt%3A%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0A%20%20%20%20%20%20%20%20prefix%20wikibase%3A%20%3Chttp%3A%2F%2Fwikiba.se%2Fontology%23%3E%0A%0A%0A%20%20%20%20%20%20%20%20SELECT%20%3FxLabel%20%3Fx%20%3FsomebodyLabel%20%3Fsomebody%20%3FotherLocation%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20(GROUP_CONCAT(%3FclassLabel%3B%20separator%3D'%2C%20')%20AS%20%3Fclassdescription)%0A%20%20%20%20%20%20%20%20WHERE%0A%20%20%20%20%20%20%20%20%7B%0A%20%20%20%20%20%20%20%20%20%20BIND('Point({longitude}%20{latitude})'%5E%5Egeo%3AwktLiteral%20AS%20%3FcurrentLocation).%0A%20%20%20%20%20%20%20%20%20%20SERVICE%20wikibase%3Aaround%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%3Fx%20wdt%3AP625%20%3FotherLocation.%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20bd%3AserviceParam%20wikibase%3Acenter%20%3FcurrentLocation.%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20bd%3AserviceParam%20wikibase%3Aradius%20'{radius}'.%20%0A%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%20%20%23%20x%20is%20named%20after%0A%20%20%20%20%20%20%20%20%20%20%3Fx%20wdt%3AP138%20%3Fsomebody%20.%0A%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%23%20that%20somebody%20is%20a%20human%0A%20%20%20%20%20%20%20%20%20%20%3Fsomebody%20wdt%3AP31%20wd%3AQ5%20.%0A%0A%20%20%20%20%20%20%20%20%20%20%23%20which%20Class%20is%20x%20(e.g.%20Street%2C%20church)%0A%20%20%20%20%20%20%20%20%20%20%3Fx%20wdt%3AP31%20%20%3Fclass%20.%20%0A%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%23%20the%20class%20has%20a%20german%20label%20%0A%20%20%20%20%20%20%20%20%20%20%3Fclass%20rdfs%3Alabel%20%3FclassLabel%20.%0A%20%20%20%20%20%20%20%20%20%20FILTER(%20lang(%3FclassLabel)%20%3D%20%22de%22%20)%0A%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%20%20%23%20Retrieve%20Labels%0A%20%20%20%20%20%20%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22de%22.%20%7D%20%0A%20%20%20%20%20%20%20%20%20%20%0A%20%20%20%20%20%20%20%20%7D%20%0A%20%20%20%20%20%20%20%20GROUP%20BY%20%3FxLabel%20%3Fx%20%3FsomebodyLabel%20%3Fsomebody%20%3FotherLocation%0A%20%20%20%20%20%20%20%20LIMIT%20{limit}%0A%20%20%20%20%20%20%20%20'''.format(
        longitude=longitude, latitude=latitude, radius=radius, limit=limit)

    return map_


def create_abstract_level2(somebody, somebodys_name):
    query = '''
            prefix owl:  <http://www.w3.org/2002/07/owl#>
            prefix dbo:  <http://dbpedia.org/ontology>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?comment # ?abstract 

            WHERE {{
                 ?s owl:sameAs <{somebody}> .
                 ?s rdfs:comment ?comment.
                 FILTER( lang(?comment) = "en" )

                 #?s dbo:abstract ?abstract .
                 #FILTER( lang(?abstract) = "en" )

            }}
            '''.format(somebody=somebody)

    # Initializing SPARQL Wrapper and querying
    endpoint = 'http://dbpedia.org/sparql'
    sparql = SPARQLWrapper(endpoint, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()

    # Trying to retrieve the comment. In case there is none or the person was not found. Return the error message.
    try:
        abstract = result['results']['bindings'][0]['comment']['value']
    except:
        abstract = 'Sorry, there is no description of {}.'.format(somebodys_name)

    return abstract


def create_df_level2(somebody, current_latitude, current_longitude):
    query = '''
        prefix bd:       <http://www.bigdata.com/rdf#>
        prefix wd:       <http://www.wikidata.org/entity/>
        prefix wdt:      <http://www.wikidata.org/prop/direct/>
        prefix wikibase: <http://wikiba.se/ontology#>


        SELECT ?x ?xLabel ?somebodyLabel ?Location ?countryLabel
            (GROUP_CONCAT(?classLabel; separator=', ') AS ?Description)

        WHERE {{
          # x is named after
          ?x wdt:P138 <{somebody}> ;

          # x has location
             wdt:P625 ?Location ;

          # which Class is x (e.g. Street, church)
             wdt:P31  ?class . 
          
          # get somebodys name (needed to display name on top of level 2)
          ?x wdt:P138 ?somebody.

          # the class has a german label 
          ?class rdfs:label ?classLabel .
          FILTER ( lang(?classLabel) = "de" )

          # located in Germany, Austria, or Switzerland
          ?x wdt:P17 ?country .
          FILTER ( ?country = wd:Q39 || ?country = wd:Q40 || ?country = wd:Q183 )

          # Retrieve Labels
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de". }}

        }}
        GROUP BY ?x ?xLabel ?somebodyLabel ?Location ?countryLabel
        LIMIT 1000

    '''.format(somebody=somebody)

    # Initializing SPARQL Wrapper and querying
    endpoint = 'https://query.wikidata.org/sparql'
    sparql = SPARQLWrapper(endpoint, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Results
    df = pd.DataFrame(results['results']['bindings'])
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x['value'])

    # Compute distance
    df['Distance (km)'] = df['Location'].apply(lambda point: compute_distance(new_point=point,
                                                                              current_longitude=current_longitude,
                                                                              current_latitude=current_latitude))

    # Sort according to distance
    df.sort_values(by=['Distance (km)'], inplace=True)

    # Rename columns
    df.rename(columns={"xLabel": "Object", "somebodyLabel": "Person", "countryLabel": "Country",
                       "Location": "Object Location"}, inplace=True)

    return df


def create_map_level2(somebody):
    map_ = '''https://query.wikidata.org/embed.html#%20%20%20%20%23defaultView%3AMap%0A%20%20%20%20prefix%20bd%3A%20%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.bigdata.com%2Frdf%23%3E%0A%20%20%20%20prefix%20wd%3A%20%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%0A%20%20%20%20prefix%20wdt%3A%20%20%20%20%20%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0A%20%20%20%20prefix%20wikibase%3A%20%3Chttp%3A%2F%2Fwikiba.se%2Fontology%23%3E%0A%0A%0A%20%20%20%20SELECT%20%3Fx%20%3FxLabel%20%3FLocation%20%3FcountryLabel%0A%20%20%20%20%20%20%20%20(GROUP_CONCAT(%3FclassLabel%3B%20separator%3D'%2C%20')%20AS%20%3Fclassdescription)%0A%0A%20%20%20%20WHERE%20%7B%0A%20%20%20%20%20%20%23%20x%20is%20named%20after%0A%20%20%20%20%20%20%3Fx%20wdt%3AP138%20<{somebody}>%20%3B%0A%0A%20%20%20%20%20%20%23%20x%20has%20location%0A%20%20%20%20%20%20%20%20%20wdt%3AP625%20%3FLocation%20%3B%0A%0A%20%20%20%20%20%20%23%20which%20Class%20is%20x%20(e.g.%20Street%2C%20church)%0A%20%20%20%20%20%20%20%20%20wdt%3AP31%20%20%3Fclass%20.%20%0A%0A%20%20%20%20%20%20%23%20the%20class%20has%20a%20german%20label%20%0A%20%20%20%20%20%20%3Fclass%20rdfs%3Alabel%20%3FclassLabel%20.%0A%20%20%20%20%20%20FILTER%20(%20lang(%3FclassLabel)%20%3D%20%22de%22%20)%0A%0A%20%20%20%20%20%20%23%20located%20in%20Germany%2C%20Austria%2C%20or%20Switzerland%0A%20%20%20%20%20%20%3Fx%20wdt%3AP17%20%3Fcountry%20.%0A%20%20%20%20%20%20FILTER%20(%20%3Fcountry%20%3D%20wd%3AQ39%20%7C%7C%20%3Fcountry%20%3D%20wd%3AQ40%20%7C%7C%20%3Fcountry%20%3D%20wd%3AQ183%20)%0A%0A%20%20%20%20%20%20%23%20Retrieve%20Labels%0A%20%20%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22de%22.%20%7D%0A%0A%20%20%20%20%7D%0A%20%20%20%20GROUP%20BY%20%3Fx%20%3FxLabel%20%3FLocation%20%3FcountryLabel%0A%20%20%20%20LIMIT%201000'''.format(
        somebody=somebody)

    return map_


def compute_distance(new_point, current_longitude, current_latitude):
    new_location = np.array([float(x) for x in new_point[6:-1].split(' ')][::-1])
    current_location = np.array([float(current_longitude), float(current_latitude)][::-1])
    distance = round(hs.haversine(new_location, current_location), 2)
    return distance
