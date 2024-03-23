from SPARQLWrapper import SPARQLWrapper, CSV
endpoint = "http://localhost:3030/Roboprof/sparql"
sparql = SPARQLWrapper(endpoint)

query = """
# QUERIES
"""

sparql.setQuery(query)
sparql.setReturnFormat(CSV)
results = sparql.query().convert()
with open("q13.csv", "wb") as f:
    f.write(results)
print("Query results saved")
