import os
import pandas as pd
import spacy
from pathlib import Path

def load_nlp_model():
    return spacy.load('en_core_web_sm')

def read_and_process_text(file_path, nlp):
    with open(file_path, 'r', encoding="UTF-8") as file:
        text = file.read()
    return nlp(text)

def append_to_dataframe(course_id, doc_type, lecture_id, spacy_doc, dataframe):
    for ent in spacy_doc.ents:
        dataframe.append({
            'CourseId': course_id,
            'Type': doc_type,
            'Identifier': lecture_id,
            'Topic Name': ent.text,
            'Topic Link': 'No link available',
            'Entity Type': ent.label_
        })

def process_directory(course_id, doc_type, directory, dataframe, nlp):
    for count, txtfile in enumerate(os.listdir(directory), start=1):
        file_path = directory / txtfile
        try:
            spacy_doc = read_and_process_text(file_path, nlp)
            append_to_dataframe(course_id, doc_type, count, spacy_doc, dataframe)
            print(f"Processed {txtfile}")
        except Exception as e:
            print(f"Error processing {txtfile}: {e}")

def main():
    base_dir = Path.cwd() / "Generator"
    courses = {
        'COMP6741': {'CourseId': '40355', 'Directories': ['Lecture', 'Worksheet']},
        'COMP6721': {'CourseId': '40353', 'Directories': ['Lecture', 'Worksheet']}
    }

    # Initialize Spacy NLP model
    nlp = load_nlp_model()
    data_entries = []

    for course, details in courses.items():
        for directory in details['Directories']:
            full_dir = base_dir / course / directory
            process_directory(details['CourseId'], directory, full_dir, data_entries, nlp)

    df = pd.DataFrame(data_entries)
    print(df.head())
    df.to_csv(base_dir / 'Topic.csv', index=False)

if __name__ == "__main__":
    main()