import yaml
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from SPARQLWrapper import SPARQLWrapper, JSON

# Load SPARQL queries from a YAML file
def load_queries():
    with open('queries.yml') as file:
        return yaml.safe_load(file)

queries = load_queries()

# General method to run SPARQL queries
def run_query(query, **kwargs):
    sparql = SPARQLWrapper("http://localhost:3030/dataset/query")
    formatted_query = query.format(**kwargs)
    sparql.setQuery(formatted_query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

# Define an action for each intent that requires a SPARQL query
class ActionQueryUniversityCourses(Action):
    def name(self):
        return "action_query_university_courses"

    def run(self, dispatcher, tracker, domain):
        university = tracker.get_slot('university')
        query = queries['queries']['list_university_courses']['query']
        results = run_query(query, university=university)

        courses = [result['course']['value'] for result in results['results']['bindings']]
        message = f"{university} offers the following courses: " + ", ".join(courses)
        dispatcher.utter_message(text=message)
        return []

# Additional actions can be defined following the same pattern.
