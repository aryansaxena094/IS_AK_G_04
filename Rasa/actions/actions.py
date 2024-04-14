from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from SPARQLWrapper import SPARQLWrapper, JSON

class ActionGetCourseDescription(Action):
    def name(self):
        return "action_get_course_description"

    def run(self, dispatcher, tracker, domain):
        course_name = tracker.get_slot('course')
        # Your SPARQL query here
        # Query the Fuseki server and fetch the course description
        # Format the response and send it back to the user
        dispatcher.utter_message(text=f"The course {course_name} is about ...")
        return []