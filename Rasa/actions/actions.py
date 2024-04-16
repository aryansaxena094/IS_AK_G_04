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

# 1. List Universities Query
class ActionListUniversityCourses(Action):
    def name(self):
        return "action_list_university_courses"

    def run(self, dispatcher, tracker, domain):
        university = tracker.get_slot('university').replace(" ", "_")
        print("Running function: action_list_university_courses")
        print(f"University: {university}")

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

# 2. List Courses Query Using A Topic
class ActionFindCoursesByTopic(Action):
    def name(self):
        return "action_find_courses_by_topic"

    def run(self, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')
        print("Running function: action_find_courses_by_topic")
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

# 3. List Topics In A Course Query During Event
class ActionListTopicsInCourseDuringEvent(Action):
    def name(self):
        return "action_list_topics_in_course_during_event"

    def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot('course_code')  # e.g., "COMP 6641"
        subject = tracker.get_slot('subject')
        lecture_number = tracker.get_slot('event')  # e.g., "lecture 2"
        print("Running function: action_list_topics_in_course_during_event")
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
                                ex:lectureOfCourse ?course ;
                                ex:lectureNumber {lecture_number} .
                        ?topic ex:isTopicOfLecture ?lecture ;
                            ex:isTopicOfCourse ?course ;
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

# 4. List Courses By Subject Query
class ActionListTopicsBySubject(Action):
    def name(self):
        return "action_list_courses_by_subject"

    def run(self, dispatcher, tracker, domain):
        subject = tracker.get_slot('subject')  # e.g., "SOEN"
        print("Running function: action_list_courses_by_subject")
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

# 5. Distinct Lecture Name for a Course for a TOPIC
class ActionRecommendedMaterialsForTopic(Action):
    def name(self):
        return "action_recommended_materials_for_topic"
    
    def run(self, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')
        number = tracker.get_slot('course_number')
        subject = tracker.get_slot('subject')
        print("Running function: action_recommended_materials_for_topic")
        print(f"Topic: {topic}, Subject: {subject}, Number: {number}")
        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT DISTINCT ?lectureName
            WHERE {{
            # Select the specific course by subject and number
            ?course a ex:Course;
                    ex:subject "{subject}"^^xsd:string;
                    ex:number "{number}"^^xsd:string.

            # Find topics that are part of this course
            ?topic a ex:Topic;
                    ex:isTopicOfCourse ?course;
                    ex:topicName "{topic}"^^xsd:string.  # Adjust topic name as necessary

            # Find lectures that include this topic
            ?topic ex:isTopicOfLecture ?lecture.
            
            # Get the names of these lectures
            ?lecture ex:lectureName ?lectureName.
            }}
        """
        # Result will be like: Lecture name - "Lecture 1", "Lecture 2", etc.
        results = run_query(query)
        if results and results['results']['bindings']:
            lectures = [result['lectureName']['value'] for result in results['results']['bindings']]
            message = f"The following lectures cover the topic {topic}: " + ", ".join(lectures)
        else:
            message = f"No lectures were found for the topic {topic}."
        dispatcher.utter_message(text=message)
        return []

# 6. Getting Course Credits
class ActionCourseCredits(Action):
    def name(self):
        return "action_course_credits"
    
    def run(self, dispatcher, tracker, domain):
        subject = tracker.get_slot('subject')
        number = tracker.get_slot('course_number')
        course = f"{subject} {number}"
        print("Running function: action_course_credits")
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


# 7. Getting Additional Course Resources using seeAlso, querying course using subject+number
class ActionAdditionalCourseResources(Action):
    def name(self):
        return "action_additional_course_resources"
    
    def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot('course_number')
        subject = tracker.get_slot('subject')
        print("Running function: action_additional_course_resources")
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

# 8. Getting MATERIALS (name, link, type) for a course in a lecture
class ActionDetailCourseContent(Action):
    def name(self):
        return "action_detail_course_content"
    
    def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot('course_number')
        subject = tracker.get_slot('subject')
        lecture = tracker.get_slot('lecture')
        lecture_number = ''.join(filter(str.isdigit, lecture))
        print("Running function: action_detail_course_content")
        print(f"Subject: {subject}, Number: {number}, Lecture: {lecture}, Lecture Number: {lecture_number}")

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?topicName ?topicLink ?materialType
            WHERE {{
            ?course a ex:Course;
                    ex:subject "{subject}"^^xsd:string;  
                    ex:number "{number}"^^xsd:string.   

            ?lecture a ex:Lecture;
                    ex:lectureOfCourse ?course;
                    BIND (IRI(CONCAT("http://example.org/vocab/lecture/", "{lecture_number}")) AS ?specificLecture)

            ?topic ex:isTopicOfLecture ?specificLecture;
                    a ex:Topic;
                    ex:topicName ?topicName;
                    ex:materialType ?materialType. 

            BIND (IRI(?topic) AS ?topicLink)
            }}
        """
        # Result will be like: 00038(topicName) <http://dbpedia.org/resource/00038>(topicLink) Lecture (materialType)
        results = run_query(query)
        if results and results['results']['bindings']:
            materials = [(result['topicName']['value'], result['topicLink']['value'], result['materialType']['value']) for result in results['results']['bindings']]
            message = f"Here are the materials for the lecture {lecture} in course {subject} {number}: \n"
            for material in materials:
                message += f"Topic: {material[0]}, Link: {material[1]}, Type: {material[2]}\n"
        else:
            message = f"No materials were found for the lecture {lecture} in course {subject} {number}."
    

# 9. Getting lecture Number, and material type for a course for a topic
class ActionRecommendedReadingForTopic(Action):
    def name(self):
        return "action_recommended_reading_for_topic"
    
    def run(self, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')
        number = tracker.get_slot('course_number')
        subject = tracker.get_slot('subject')
        print("Running function: action_recommended_reading_for_topic")
        print(f"Topic: {topic}, Subject: {subject}, Number: {number}")

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?lectureNumber ?materialType
            WHERE {{
            # Identifying the specific course by subject and number
            ?course a ex:Course;
                    ex:subject "{subject}"^^xsd:string;  # Specify the course subject
                    ex:number "{number}"^^xsd:string.   # Specify the course number

            # Finding topics associated with this course and matching a specified topic name
            ?topic a ex:Topic;
                    ex:topicName "{topic}"^^xsd:string;  # Specify the topic of interest
                    ex:isTopicOfCourse ?course.

            # Getting lecture numbers and material types linked to the topic
            ?topic ex:isTopicOfLecture ?lecture;
                    ex:materialType ?materialType.

            # Extracting lecture number from the lecture URI
            BIND(REPLACE(STR(?lecture), "http://example.org/vocab/lecture/", "") AS ?lectureNumber)
            }}
        """
        # Result will be like: 1(lectureNumber) Lecture(materialType)
        results = run_query(query)
        if results and results['results']['bindings']:
            lectures = [(result['lectureNumber']['value'], result['materialType']['value']) for result in results['results']['bindings']]
            message = f"The following lectures cover the topic {topic}: \n"
            for lecture in lectures:
                message += f"Lecture {lecture[0]} - {lecture[1]}\n"
        else:
            message = f"No lectures were found for the topic {topic}."

# 10. Gettting Competencies Gained for a course
class ActionCompetenciesGained(Action):
    def name(self):
        return "action_competencies_gained"
    
    def run(self, dispatcher, tracker, domain):
        subject = tracker.get_slot('subject')
        number = tracker.get_slot('course_number')
        course = f"{subject} {number}"
        print("Running function: action_competencies_gained")
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

# 11. Getting Grades of person in a course
class ActionStudentGrades(Action):
    def name(self):
        return "action_student_grades"
    
    def run(self, dispatcher, tracker, domain):
        person = tracker.get_slot('person')
        subject = tracker.get_slot('subject')
        number = tracker.get_slot('course_number')
        coursev = f"{subject} {number}"
        print("Running function: action_student_grades")
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

# 12. Getting students who have completed a particular course
class ActionStudentCompletedCourses(Action):
    def name(self):
        return "action_student_completed_courses"
    
    def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot('course_number')
        subject = tracker.get_slot('subject')
        print("Running function: action_student_completed_courses")
        print(f"Subject: {subject}, Number: {number}")

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?studentName
            WHERE {{
            ?student a ex:Student;
                    ex:completedCourse ?completedCourse.
            ?completedCourse ex:course ?course.
            ?course ex:number "{number}"^^xsd:string;
                    ex:subject "{subject}".
            ?student foaf:name ?studentName.
            }}
        """
        # Result will be the names of the students who have completed the course
        result = run_query(query)
        if result and result['results']['bindings']:
            students = [r['studentName']['value'] for r in result['results']['bindings']]
            message = f"The following students have completed the course {subject} {number}: " + ", ".join(students)
        else:
            message = f"No students were found who have completed the course {subject} {number}."

# 13. Getting transcript of a student
class ActionStudentTranscript(Action):
    def name(self):
        return "print_student_transcript"
    
    def run(self, dispatcher, tracker, domain):
        person = tracker.get_slot('person')
        print("Running function: print_student_transcript")
        print(f"Person: {person}")

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?courseName ?courseID ?grade
            WHERE {{
            # Find the student by name
            ?student a ex:Student;
                    foaf:name "{person}"^^xsd:string.

            # Find completed courses and corresponding grades
            ?student ex:completedCourse ?compCourse .
            ?compCourse ex:course ?course ;
                        ex:courseGrade ?grade .
            
            # Retrieve course details
            ?course ex:subject ?subject ;
                    ex:number ?number ;
                    ex:description ?description .
            
            # Bind variables for course name and course ID
            BIND (?description AS ?courseName)
            BIND (CONCAT(?subject, ?number) AS ?courseID)
            }}
        """
        # Result will be like : OPERATING SYSTEMS(courseName) COMP5461(courseID) B+(grade)
        results = run_query(query)

        if results and results['results']['bindings']:
            transcript = [(result['courseName']['value'], result['courseID']['value'], result['grade']['value']) for result in results['results']['bindings']]
            message = f"Transcript for {person}:\n"
            for course in transcript:
                message += f"Course: {course[0]}, Course ID: {course[1]}, Grade: {course[2]}\n"
        else:
            message = f"No transcript was found for {person}."
        dispatcher.utter_message(text=message)
        return []


# 14.
class ActionCourseDescription(Action):
    def name(self):
        return "action_course_description"
    
    def run(self, dispatcher, tracker, domain):
        subject = tracker.get_slot('subject')
        number = tracker.get_slot('course_number')
        print("Running function: action_course_description")
        print(f"Subject: {subject}, Number: {number}")

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT ?description
            WHERE {{
            ?course a ex:Course;
                    ex:subject "{subject}"^^xsd:string; 
                    ex:number "{number}"^^xsd:string; 
                    ex:description ?description.
            }}
        """
        # Result will be the description (APPLIED ARTIFICIAL INTELLIGENCE) of the course
        results = run_query(query)

        if results and results['results']['bindings']:
            description = results['results']['bindings'][0]['description']['value']
            message = f"The course {subject} {number} is described as: {description}"
        else:
            message = f"An error occurred while fetching course description."
        dispatcher.utter_message(text=message)
        return []
    
# 15.
class ActionTopicsCoveredInCourseEvent(Action):
    def name(self):
        return "action_topics_covered_in_course_event"
    
    def run(self, dispatcher, tracker, domain):
        event = tracker.get_slot('event')
        subject = tracker.get_slot('subject')
        number = tracker.get_slot('course_number')
        print("Running function: action_topics_covered_in_course_event")
        print(f"Event: {event}, Subject: {subject}, Number: {number}")
        lectureNumber = ''.join(filter(str.isdigit, event))

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?topicName ?topicLink
            WHERE {{
            ?course a ex:Course;
                    ex:subject "{subject}"^^xsd:string;
                    ex:number "{number}"^^xsd:string.
            
            ?lecture a ex:Lecture;
                    ex:lectureNumber {lectureNumber} ;
                    ex:lectureOfCourse ?course.
            
            ?topic a ex:Topic;
                    ex:topicName ?topicName;
                    ex:isTopicOfLecture ?lecture.
            BIND (STR(?topic) AS ?topicLink)
            }}
        """

        # Result wil be A12(topicName) http://dbpedia.org/resource/A12(topicLink)
        result = run_query(query)

        if result and result['results']['bindings']:
            topics = [(r['topicName']['value'], r['topicLink']['value']) for r in result['results']['bindings']]
            message = f"The topics covered in the event {event} of course {subject} {number} are: \n"
            for topic in topics:
                message += f"Topic: {topic[0]}, Link: {topic[1]}\n"
        else:
            message = f"No topics were found for the event {event} of course {subject} {number}."
        dispatcher.utter_message(text=message)
        return []

# 16.
class ActionEventsCoveringTopic(Action):
    def name(self):
        return "action_events_covering_topic"
    
    def run(self, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')
        print("Running function: action_events_covering_topic")
        print("Topic: ", topic)

        query = """
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?course ?materialType ?Name
            WHERE {{
            ?topic ex:topicName "CNN"^^xsd:string;
                    ex:isTopicOfLecture ?lecture;
                    ex:materialType ?materialType.
            ?lecture a ex:Lecture;
                    ex:lectureName ?Name;
                    ex:lectureOfCourse ?course.
            ?course a ex:Course;
                    ex:description ?courseDescription.
            }}
            ORDER BY DESC(?materialType) 
        """

        # Result will be - <http://example.org/vocab/course/40353>(course) Worksheet(materialType) Deep Learning for Intelligent Systems(name)
        results = run_query(query)

        if results and results['results']['bindings']:
            events = [(result['course']['value'], result['materialType']['value'], result['Name']['value']) for result in results['results']['bindings']]
            message = f"The following events cover the topic {topic}: \n"
            for event in events:
                message += f"Course: {event[0]}, Material Type: {event[1]}, Name: {event[2]}\n"
        else:
            message = f"No events were found for the topic {topic}."
        dispatcher.utter_message(text=message)
        return []
    
# 17.
class ActionListTopicsInCourse(Action):
    def name(self):
        return "action_list_topics_in_course"
    
    def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot('course_number')
        subject = tracker.get_slot('subject')
        print("Running function: action_list_topics_in_course")
        print(f"Subject: {subject}, Number: {number}")

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT DISTINCT ?topicName ?lectureUri ?resourceUri
            WHERE {{
            ?course a ex:Course;
                    ex:number "{number}";   
                    ex:subject "{subject}".  
            ?topicUri a ex:Topic;
                        ex:topicName ?topicName;
                        ex:isTopicOfCourse ?course;
                        ex:materialType ?material;
                        ex:isTopicOfLecture ?lectureUri.
            ?lectureUri ex:lectureNumber ?lectureNum.
            BIND(CONCAT(?material, STR(?lectureNum)) AS ?resourceUri)
            }}
        """

        # Result will be - TopicName, LectureUri, ResourceUri
        results = run_query(query)

        if results and results['results']['bindings']:
            topics = [(result['topicName']['value'], result['lectureUri']['value'], result['resourceUri']['value']) for result in results['results']['bindings']]
            message = f"The topics covered in the course {subject} {number} are: \n"
            for topic in topics:
                message += f"Topic: {topic[0]}, Lecture: {topic[1]}, Resource: {topic[2]}\n"
        else:
            message = f"No topics were found for the course {subject} {number}."
        dispatcher.utter_message(text=message)
        return []

# 18.
class ActionCountTopicOccurances(Action):
    def name(self):
        return "action_count_topic_occurances"
    
    def run(self, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')
        subject = tracker.get_slot('subject')
        number = tracker.get_slot('course_number')
        print("Running function: action_count_topic_occurances")
        print(f"Topic: {topic}, Subject: {subject}, Number: {number}")

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?course ?courseDescription (COUNT(?lecture) AS ?numberOfOccurrences)
            WHERE {{
            ?topic a ex:Topic;
            ex:topicName "{topic}".
            ?topic ex:isTopicOfCourse ?course.
            ?topic ex:isTopicOfLecture ?lecture.
            ?course a ex:Course;
                    ex:subject "{subject}";
                    ex:number "{number}";
                    ex:description ?courseDescription.
            }}
            GROUP BY ?course ?courseDescription
            ORDER BY DESC(?numberOfOccurrences)
        """
        # result will be - <http://example.org/vocab/course/40353>(course) Deep Learning for Intelligent Systems(courseDescription) 2(numberOfOccurrences)
        results = run_query(query)

        if results and results['results']['bindings']:
            occurrences = [(result['course']['value'], result['courseDescription']['value'], result['numberOfOccurrences']['value']) for result in results['results']['bindings']]
            message = f"The topic {topic} occurs in the following courses: \n"
            for occurrence in occurrences:
                message += f"Course: {occurrence[0]}, Description: {occurrence[1]}, Number of Occurrences: {occurrence[2]}\n"
        else:
            message = f"No occurrences were found for the topic {topic}."
        dispatcher.utter_message(text=message)
        return []
    
# 19.
class ActionListDescriptionAndInfoForTopic(Action):
    def name(self):
        return "action_list_description_and_info_for_topic"
    
    def run(self, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')
        print("Running function: action_list_description_and_info_for_topic")
        print("Topic: ", topic)

        query = f"""
            PREFIX ex: <http://example.org/vocab/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?courseDescription ?lectureFormat ?lectureNumber
            WHERE {{
            ?topicUri a ex:Topic;
                        ex:isTopicOfCourse ?courseUri;
                        ex:isTopicOfLecture ?lectureUri;
                        ex:topicName "{topic}";
                        ex:materialType ?material.
            ?courseUri ex:description ?courseDescription.
            ?lectureUri ex:lectureNumber ?lectureNumber.

            # Adjust the output format for lecture/material type.
            BIND (IF(CONTAINS(STR(?material), "Lecture"), CONCAT("Lecture ", STR(?lectureNumber)), 
                    IF(CONTAINS(STR(?material), "Worksheet"), CONCAT("Worksheet ", STR(?lectureNumber)), STR(?material))) AS ?lectureFormat)
            }}
        """

        # Result will be - CourseDescription, LectureFormat, LectureNumber
        results = run_query(query)

        if results and results['results']['bindings']:
            info = [(result['courseDescription']['value'], result['lectureFormat']['value'], result['lectureNumber']['value']) for result in results['results']['bindings']]
            message = f"Here is the information for the topic {topic}: \n"
            for i in info:
                message += f"Course Description: {i[0]}, Lecture Format: {i[1]}, Lecture Number: {i[2]}\n"
        else:
            message = f"No information was found for the topic {topic}."
        dispatcher.utter_message(text=message)
        return []

# 20.
class ActionNoMaterialForCourses(Action):
    def name(self):
        return "action_no_material_for_courses"
    
    def run(self, dispatcher, tracker, domain):
        print("Running function: action_no_material_for_courses")

        query = f"""
            PREFIX ex: <http://example.org/vocab/>

            SELECT ?courseCode
            WHERE {{
            ?courseUri a ex:Course;
                        ex:number ?number;
                        ex:subject ?subject.

            # Construct course code from subject and number
            BIND(CONCAT(?subject, " ", ?number) AS ?courseCode)

            # Check if there is no topic linked to this course
            FILTER NOT EXISTS {{
                ?topicUri a ex:Topic;
                        ex:isTopicOfCourse ?courseUri.
            }}
            }}
        """

        # Result will be - COMP 5461(courseCode)
        results = run_query(query)

        if results and results['results']['bindings']:
            courses = [result['courseCode']['value'] for result in results['results']['bindings']]
            message = f"The following courses have no material associated with them: " + ", ".join(courses)
        else:
            message = f"No courses were found with no material associated with them."
        dispatcher.utter_message(text=message)
        return []