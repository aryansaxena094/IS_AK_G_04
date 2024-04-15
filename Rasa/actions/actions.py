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
        number = tracker.get_slot('course_code')  # e.g., "COMP 6641"
        subject = tracker.get_slot('subject')
        lecture_number = tracker.get_slot('event')  # e.g., "lecture 2"
        print(f"Subject: {subject}, Number: {number}, Lecture Number: {lecture_number}")
        if lecture_number:
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
                    message = f"The course {subject}{number} in lecture {lecture_number} covers the following topics: " + ", ".join(topics)
                else:
                    message = f"No topics were found for the course {subject}{number} in lecture {lecture_number}."
        else:
            message = "No information found."
        dispatcher.utter_message(text=message)
        return []


class ActionListTopicsBySubject(Action):
    def name(self):
        return "action_list_courses_by_subject"

    def run(self, dispatcher, tracker, domain):
        print("Action triggered: action_list_courses_by_subject")
        subject = tracker.get_slot('subject')  # e.g., "SOEN"
        print("Subject: ", subject)
        if subject:
            query = f"""
                PREFIX ex: <http://example.org/vocab/>
                PREFIX dbo: <http://dbpedia.org/ontology/>

                SELECT ?subject ?number ?description
                WHERE {{
                  ?university dbo:offersCourse ?course .
                  ?course a ex:Course ;
                          ex:subject ?subject ;
                          ex:number ?number ;
                          ex:description ?description .
                  FILTER(?subject = "{subject}")
                }}
            """
            
            result = run_query(query)
            if result and result['results']['bindings']:
                courses_info = [(r['subject']['value'], r['number']['value'], r['description']['value']) for r in result['results']['bindings']]
                message = "The following courses are offered by universities and have the subject code {}:\n".format(subject)
                for course_info in courses_info:
                    message += f"Subject: {course_info[0]}, Number: {course_info[1]}, Description: {course_info[2]}\n"
            else:
                message = f"No courses were found for the subject {subject}."
        else:
            message = "Please provide the subject code to list the courses."
        
        dispatcher.utter_message(text=message)
        return []

# class ActionRecommendedMaterialsForTopic(Action):
#     def name(self):
#         return "action_recommended_materials_for_topic"
    
#     def run(self, dispatcher, tracker, domain):
#         topic = tracker.get_slot('subject')


class ActionCourseCredits(Action):
    def name(self):
        return "action_course_credits"
    
    def run(self, dispatcher, tracker, domain):
        course = tracker.get_slot('course')
        course_split = course.split(" ")
        subject = course_split[0]
        number = course_split[1]
        print(f"Subject: {subject}, Number: {number}")
        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            SELECT ?credits
            WHERE {{
            ?course a ex:Course ;
                    ex:subject "{subject}" ;
                    ex:number "{number}";
                    ex:credits ?credits .
            }}
        """
        results = run_query(query)
        if results and results['results']['bindings']:
            credits = results['results']['bindings'][0]['credits']['value']
            message = f"The course {course} is worth {credits} credits."
        else:
            message = f"An error occurred while fetching course credits."
        dispatcher.utter_message(text=message)
        return []


class ActionAdditionalCourseResources(Action):
    def name(self):
        return "action_additional_course_resources"
    
    def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot('course_number')
        subject = tracker.get_slot('subject')
        print(f"Subject: {subject}, Number: {number}")
        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?lectureName
            WHERE {{
            ?lecture a ex:Lecture ;
                    ex:isPartOfCourse ?course ;
                    ex:lectureName ?lectureName .
            ?course ex:subject "{subject}"^^xsd:string ;
                    ex:number "{number}"^^xsd:string .
            }}
        """
        results = run_query(query)
        if results and results['results']['bindings']:
            resources = [result['lectureName']['value'] for result in results['results']['bindings']]
            message = f"Here are some additional resources(lectures) for the course {subject} {number}: " + ", ".join(resources)
        else:
            message = f"No additional resources were found for the course {subject} {number}."


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

class ActionCompetenciesGained(Action):
    def name(self):
        return "action_competencies_gained"
    
    def run(self, dispatcher, tracker, domain):
        course = tracker.get_slot('course')
        course_split = course.split(" ")
        subject = course_split[0]
        number = course_split[1]
        print(f"Subject: {subject}, Number: {number}")
        query = f"""
            PREFIX ex: <http://example.org/vocab/>

            SELECT ?topic ?subject ?number
            WHERE {{
            ?student ex:completedCourse ?completedCourse .
            ?completedCourse ex:course ?course .
            ?course ex:subject "{subject}" .  
            ?course ex:number "{number}" .
            ?student ex:hasCompetency ?competency .
            ?competency ex:subject ?subject .
            ?competency ex:number ?number .
            }}
        """
        results = run_query(query)
        if results and results['results']['bindings']:
            competencies = []
            for r in results['results']['bindings']:
                competency_subject = r['subject']['value']
                competency_number = r['number']['value']
                competencies.append(f"{competency_subject} {competency_number}")
            message = f"Upon completion of the course {course}, you will have gained the following competencies: " + ", ".join(competencies)
        else:
            message = f"An error occurred while fetching competencies gained."
        dispatcher.utter_message(text=message)
        return []

class ActionStudentGrades(Action):
    def name(self):
        return "action_student_grades"
    
    def run(self, dispatcher, tracker, domain):
        person = tracker.get_slot('person')
        coursev = tracker.get_slot('course')
        course_split = coursev.split(" ")
        subject = course_split[0]
        number = course_split[1]
        print(f"Person: {person}, Subject: {subject}, Number: {number}")
        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            SELECT ?grade
            WHERE {{
                ?student ex:completedCourse ?compCourse .
                ?compCourse ex:course ?course ;
                            ex:courseGrade ?grade .
                ?course ex:number "{number}"^^xsd:string ;
                        ex:subject "{subject}"^^xsd:string .
                ?student foaf:name "{person}"^^xsd:string .
            }}
        """
        results = run_query(query)
        if results and results['results']['bindings']:
            grades = [r['grade']['value'] for r in results['results']['bindings']]
            message = f"The grades for {person} in course {coursev} are: " + ", ".join(grades)
        else:
            message = f"An error occurred while fetching grades."
        dispatcher.utter_message(text=message)
        return []

class ActionStudentCompletedCourses(Action):
    def name(self):
        return "action_student_completed_courses"
    
    def run(self, dispatcher, tracker, domain):
