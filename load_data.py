import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD
import urllib.parse

# Initialize Graph
g = Graph()

# Define Namespaces
ex = Namespace("http://example.org/vocab/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

# Bind namespace prefixes
g.bind("ex", ex)
g.bind("foaf", foaf)
g.bind("rdf", rdf)
g.bind("rdfs", rdfs)
g.bind("xsd", xsd)

# Load CSV
catalog_df = pd.read_csv('Concordia_Data/data.csv', encoding='utf-16')

for index, row in catalog_df.iterrows():
    course_id_str = str(row['Course ID'])
    course_uri = URIRef(f"http://example.org/vocab/course/{urllib.parse.quote(course_id_str)}")

    g.add((course_uri, RDF.type, ex.Course))
    g.add((course_uri, ex.subject, Literal(row['Subject'], datatype=XSD.string)))
    g.add((course_uri, ex.number, Literal(row['Catalog'], datatype=XSD.string)))
    g.add((course_uri, ex.description, Literal(row['Long Title'], datatype=XSD.string)))
    g.add((course_uri, ex.credits, Literal(row['Class Units'], datatype=XSD.decimal)))
    if not pd.isnull(row['Pre Requisite Description']):
        g.add((course_uri, ex.preRequisiteDescription, Literal(row['Pre Requisite Description'], datatype=XSD.string)))
    if not pd.isnull(row['Equivalent Courses']):
        g.add((course_uri, ex.equivalentCourses, Literal(row['Equivalent Courses'], datatype=XSD.string)))
    # Add other properties and classes as necessary

# Serialize the graph
g.serialize(destination='Data/roboprof_data.ttl', format='turtle')