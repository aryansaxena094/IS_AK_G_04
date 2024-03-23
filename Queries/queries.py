from SPARQLWrapper import SPARQLWrapper, CSV

# Set up the Fuseki endpoint
endpoint = "http://localhost:3030/Roboprof/sparql"  # Replace with your Fuseki endpoint
sparql = SPARQLWrapper(endpoint)

# Define the SPARQL query
query = """
PREFIX ex: <http://example.org/vocab/>

SELECT ?courseNumber ?grade
WHERE {
  ?student ex:completedCourse ?completedCourse .
  ?completedCourse ex:course ?course ;
                   ex:courseGrade ?grade .
  ?course ex:number ?courseNumber .
  FILTER(?student = <http://example.org/vocab/student/S1001>)
}
"""

# Set the query and request format
sparql.setQuery(query)
sparql.setReturnFormat(CSV)

# Execute the query and save results to a CSV file
results = sparql.query().convert()
with open("q13.csv", "wb") as f:  # Use "wb" mode for writing binary data
    f.write(results)

print("Query results saved")
