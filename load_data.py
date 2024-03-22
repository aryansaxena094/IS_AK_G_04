import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD
import urllib

# Initialize Graph
g = Graph()

# Define Namespaces
ex = Namespace("http://example.org/ns#")

# Bind namespace prefixes
g.bind("ex", ex)

# Load CSV
catalog_df = pd.read_csv('Concordia_Data/CATALOG.csv')

for index, row in catalog_df.iterrows():
    course_uri = URIRef(f"http://example.org/ns/course/{urllib.parse.quote(row['Key'])}")
    g.add((course_uri, RDF.type, ex.Course))
    g.add((course_uri, ex.hasName, Literal(row['Title'], datatype=XSD.string)))
    if not pd.isnull(row['Description']):
        g.add((course_uri, ex.courseDescription, Literal(row['Description'], datatype=XSD.string)))
    # Continue adding other properties as per your schema

# Serialize the graph
g.serialize(destination='roboprof_data.ttl', format='turtle')