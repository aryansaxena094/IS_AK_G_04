import yaml
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON
from string import Template

# Utility function to run SPARQL queries
def run_query(query, **kwargs):
    sparql = SPARQLWrapper("http://localhost:3030/Roboprof/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return results

class ActionListUniversityCourses(Action):
    def name(self):
        return "action_list_university_courses"

    def run(self, dispatcher, tracker, domain):
        university = tracker.get_slot('university').replace(" ", "_")
        query = f"""
        PREFIX ex: <http://example.org/vocab/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        SELECT ?course ?subject ?number WHERE {{
            dbr:{university} dbo:offersCourse ?course .
            ?course ex:subject ?subject ;
                    ex:number ?number .
        }}
        """
        results = run_query(query)
        if results:
            courses = [f"{result['subject']['value']} {result['number']['value']}" for result in results['results']['bindings']]
            message = ", ".join(courses) + f" are the courses offered by {university.replace('_', ' ')}"
        else:
            message = "An error occurred while fetching university courses. Please try again later."
        
        dispatcher.utter_message(text=message)
        return []

class ActionFindCoursesByTopic(Action):
    def name(self):
        return "action_find_courses_by_topic"

    def run(self, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')
        print(f"Topic: {topic}")
        
        query = f"""
        PREFIX ex: <http://example.org/vocab/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?course ?courseName
        WHERE {{
            ?topic ex:topicName "{topic}"^^xsd:string .
            ?topic ex:isTopicOfCourse ?course .
            ?course ex:description ?courseName .
        }}
        """
        result = run_query(query)
        if result:
            courses = [f"{result['courseName']['value']}" for result in result['results']['bindings']]
            message = f"The following courses cover the topic {topic}: " + ", ".join(courses)
        else:
            message = f"No courses were found for the topic {topic}."
        dispatcher.utter_message(text=message)
        return []

class ActionListTopicsInCourse(Action):
    def name(self):
        return "action_list_topics_in_course"

    def run(self, dispatcher, tracker, domain):
        course_code = tracker.get_slot('course')  # e.g., "COMP 6641"
        lecture_number = tracker.get_slot('event')  # e.g., "lecture 2"

        if course_code and lecture_number:
            # Splitting course_code into subject and number parts
            parts = course_code.split()  # Assuming the slot value comes as "COMP 6641"
            if len(parts) == 2:
                subject, number = parts
                lecture_number = ''.join(filter(str.isdigit, lecture_number))
                print(f"Subject: {subject}, Number: {number}, Lecture Number: {lecture_number}")
                query = f"""
                    PREFIX ex: <http://example.org/vocab/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                    SELECT ?topicName
                    WHERE {{
                        ?course a ex:Course ;
                                ex:subject "{subject}"^^xsd:string ;
                                ex:number "{number}"^^xsd:string .
                        ?lecture a ex:Lecture ;
                                ex:isPartOfCourse ?course ;
                                ex:lectureNumber {lecture_number} .
                        ?topic ex:isTopicOfCourse ?course ;
                            ex:isTopicOfLecture ?lecture ;
                            ex:topicName ?topicName .
                    }}
                """
                result = run_query(query)
                if result and result['results']['bindings']:
                    topics = [f"{r['topicName']['value']}" for r in result['results']['bindings']]
                    message = f"The course {course_code} in lecture {lecture_number} covers the following topics: " + ", ".join(topics)
                else:
                    message = f"No topics were found for the course {course_code} in lecture {lecture_number}."
            else:
                message = "The course information is incomplete. Please provide both the subject code and number."
        else:
            message = "Please provide both course and lecture information to find topics."

        dispatcher.utter_message(text=message)
        return []

# class ActionListCoursesBySubject(Action):
#     def name(self):
#         return "action_list_courses_by_subject"

#     def run(self, dispatcher, tracker, domain):
#         subject = tracker.get_slot('subject')
#         query = queries['list_courses_by_subject']['query']
#         results = run_query(query, subject=subject)

#         courses = [result['course']['value'] for result in results['results']['bindings']]
#         message = f"The following courses are related to the subject {subject}: " + ", ".join(courses)
#         dispatcher.utter_message(text=message)
#         return []

# class ActionRecommendedMaterialsForTopic(Action):
#     def name(self):
#         return "action_recommended_materials_for_topic"
    
#     def run(self, dispatcher, tracker, domain):
#         topic = tracker.get_slot('topic')
#         query = queries['recommended_materials_for_topic']['query']
#         results = run_query(query, topic=topic)

#         materials = [result['material']['value'] for result in results['results']['bindings']]
#         message = f"Here are some recommended materials for the topic {topic}: " + ", ".join(materials)
#         dispatcher.utter_message(text=message)
#         return []

# class ActionCourseCredits(Action):
#     def name(self):
#         return "action_course_credits"
    
#     def run(self, dispatcher, tracker, domain):
#         course = tracker.get_slot('course')
#         query = queries['course_credits']['query']
#         results = run_query(query, course=course)

#         credits = results['results']['bindings'][0]['credits']['value']
#         message = f"The course {course} is worth {credits} credits."
#         dispatcher.utter_message(text=message)
#         return []

# class ActionAdditionalCourseResources(Action):
#     def name(self):
#         return "action_additional_course_resources"
    
#     def run(self, dispatcher, tracker, domain):
#         course = tracker.get_slot('course')
#         query = queries['additional_course_resources']['query']
#         results = run_query(query, course=course)

#         resources = [result['resource']['value'] for result in results['results']['bindings']]
#         message = f"Here are some additional resources for the course {course}: " + ", ".join(resources)
#         dispatcher.utter_message(text=message)
#         return []

# class ActionDetailCourseContent(Action):
#     def name(self):
#         return "action_detail_course_content"
    
#     def run(self, dispatcher, tracker, domain):
#         course = tracker.get_slot('course')
#         query = queries['detail_course_content']['query']
#         results = run_query(query, course=course)

#         content = results['results']['bindings'][0]['content']['value']
#         message = f"Here is the detailed content for the course {course}: {content}"
#         dispatcher.utter_message(text=message)
#         return []

# class ActionRecommendedReadingForTopic(Action):
#     def name(self):
#         return "action_recommended_reading_for_topic"
    
#     def run(self, dispatcher, tracker, domain):
#         topic = tracker.get_slot('topic')
#         query = queries['recommended_reading_for_topic']['query']
#         results = run_query(query, topic=topic)

#         readings = [result['reading']['value'] for result in results['results']['bindings']]
#         message = f"Here is some recommended reading material for the topic {topic}: " + ", ".join(readings)
#         dispatcher.utter_message(text=message)
#         return []

# class ActionCompetenciesGained(Action):
#     def name(self):
#         return "action_competencies_gained"
    
#     def run(self, dispatcher, tracker, domain):
#         course = tracker.get_slot('course')
#         query = queries['competencies_gained']['query']
#         results = run_query(query, course=course)

#         competencies = [result['competency']['value'] for result in results['results']['bindings']]
#         message = f"Upon completion of the course {course}, you will have gained the following competencies: " + ", ".join(competencies)
#         dispatcher.utter_message(text=message)
#         return []

# class ActionStudentGrades(Action):
#     def name(self):
#         return "action_student_grades"
    
#     def run(self, dispatcher, tracker, domain):
#         student = tracker.get_slot('student')
#         query = queries['student_grades']['query']
#         results = run_query(query, student=student)

#         grades = [result['grade']['value'] for result in results['results']['bindings']]
#         message = f"Here are the grades for student {student}: " + ", ".join(grades)
#         dispatcher.utter_message(text=message)
#         return []

# class ActionStudentCompletedCourses(Action):
#     def name(self):
#         return "action_student_completed_courses"
    
#     def run(self, dispatcher, tracker, domain):
#         student = tracker.get_slot('student')
#         query = queries['student_completed_courses']['query']
#         results = run_query(query, student=student)

#         courses = [result['course']['value'] for result in results['results']['bindings']]
#         message = f"Here are the courses completed by student {student}: " + ", ".join(courses)
#         dispatcher.utter_message(text=message)
#         return []

# class ActionPrintStudentTranscript(Action):
#     def name(self):
#         return "action_print_student_transcript"
    
#     # We just return the course Number and the grade of the student
#     def run(self, dispatcher, tracker, domain):
#         student = tracker.get_slot('student')
#         query = queries['student_transcript']['query']
#         results = run_query(query, student=student)

#         transcript = [f"{result['course']['value']} - {result['grade']['value']}" for result in results['results']['bindings']]
#         message = f"Here is the transcript for student {student}: " + ", ".join(transcript)
#         dispatcher.utter_message(text=message)
#         return []
