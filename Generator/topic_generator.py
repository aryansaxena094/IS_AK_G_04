import os
import pandas as pd
import spacy
from pathlib import Path

base_dir = Path.cwd()
base_dir = base_dir / "Generator/"

def generate_topics(course_id, type, lecture_id, file_path):
    try:
        nlp = spacy.load('en_core_web_sm')
        with open(file_path, 'r', encoding="UTF-8") as file:
            text = file.read()
        print(f"Reading from {file_path}, content size: {len(text)}")
        doc = nlp(text)
        spacy_dic = {ent.text: ent.label_ for ent in doc.ents}
        print(f"Spacy detected entities: {spacy_dic}")
        for term, label in spacy_dic.items():
            # Append entity to the list with a placeholder link if no DBpedia link exists
            append_to_dup(course_id, type, lecture_id, term, "No link available", label)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
def append_to_dup(course_id, type, lecture_id, topic_name, topic_link, entity_type):
    dup['CourseId'].append(course_id)
    dup['Type'].append(type)
    dup['Identifier'].append(lecture_id)
    dup['Topic Name'].append(topic_name)
    dup['Topic Link'].append(topic_link)
    dup['Entity Type'].append(entity_type)
    print(f"Appending: {topic_name}, {entity_type}")

if __name__ == "__main__":
    IS_lecture_directory = base_dir / "COMP6741/Lecture"
    IS_worksheet_directory =  base_dir / "COMP6741/Worksheet"
    dup = {
        'CourseId': [],
        'Type': [],
        'Identifier': [],
        'Topic Name': [],
        'Topic Link': [],
        'Entity Type': []
    }
    count = 1
    for txtfile in os.listdir(IS_lecture_directory):
        print(str(txtfile))
        generate_topics('40355', 'Lecture', count, os.path.join(IS_lecture_directory, txtfile))
        count += 1
    count = 1
    for txtfile in os.listdir(IS_worksheet_directory):
        print(str(txtfile))
        generate_topics('40355', 'Worksheet', count, os.path.join(IS_worksheet_directory, txtfile))
        count += 1
    df = pd.DataFrame(dup)
    print(df.head())
    df.to_csv(base_dir / 'Topic.csv', index=False)