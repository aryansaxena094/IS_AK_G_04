import pandas as pd
from uuid import uuid4
from rdflib import Graph, Literal, RDF, URIRef, Namespace, NamespaceManager
from rdflib.namespace import RDFS, DC, DCTERMS, FOAF

# Define namespaces
UNISCHEMA = Namespace("http://uni.io/schema#")
UNIDATA = Namespace("http://uni.io/data#")
DBR = Namespace("http://dbpedia.org/resource/")

# Initialize a graph
graph = Graph()
graph.bind('uni', UNISCHEMA)
graph.bind('data', UNIDATA)
graph.bind('dbr', DBR)

# Function to add data to the graph
def add_resource(data_id, data_type, attributes):
    resource_id = UNIDATA[str(uuid4())]
    graph.add((resource_id, RDF.type, UNISCHEMA[data_type]))
    for attr, value in attributes.items():
        if attr == 'link':
            graph.add((resource_id, RDFS.seeAlso, URIRef(value)))
        else:
            graph.add((resource_id, UNISCHEMA[attr], Literal(value)))
    return resource_id

# Load CSV data
topics_csv = pd.read_csv('datasets/Topics.csv')
students_csv = pd.read_csv('datasets/StudentData.csv')
lectures_csv = pd.read_csv('datasets/LectureData.csv')
data_csv = pd.read_csv('datasets/Data.csv')

# Process topics
for idx, topic in topics_csv.iterrows():
    add_resource(topic['TopicId'], 'Topic', {
        'name': topic['Name'],
        'description': topic['Description'],
        'link': topic['Link']
    })

# Process students
for idx, student in students_csv.iterrows():
    student_id = add_resource(student['StudentId'], 'Student', {
        'name': student['Name'],
        'email': student['Email']
    })
    # Assuming there's a column 'CourseId' in StudentData.csv
    if 'CourseId' in student:
        course_uri = UNIDATA[student['CourseId']]
        graph.add((student_id, UNISCHEMA.enrolledIn, course_uri))

# Process lectures
for idx, lecture in lectures_csv.iterrows():
    lecture_id = add_resource(lecture['LectureId'], 'Lecture', {
        'title': lecture['Title'],
        'date': lecture['Date']
    })
    if 'CourseId' in lecture:
        course_uri = UNIDATA[lecture['CourseId']]
        graph.add((lecture_id, UNISCHEMA.partOf, course_uri))

# Process generic data
for idx, data in data_csv.iterrows():
    add_resource(data['DataId'], 'Data', {
        'content': data['Content'],
        'type': data['Type']
    })

# Serialize the graph in Turtle format
graph.serialize('KnowledgeBase.ttl', format='turtle')
print("Graph serialized to Turtle format.")

# Optionally, serialize in N-Triples if needed
graph.serialize('KnowledgeBase.nt', format='nt')
print("Graph serialized to N-Triples format.")
