import os
import pandas as pd
import spacy
import en_core_web_sm
nlp = spacy.load('en_core_web_sm')

def generate_topics(courseID, type, lectureID, filePath):
    file = open(filePath, 'r', encoding="UTF-8")
    text = file.read()
    try:
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(text)
        

        for ent in doc.ents:
             spacyDic[ent.text] = ent.label_
        


        nlp = spacy.blank('en')
        nlp.add_pipe('dbpedia_spotlight')
        doc=nlp(text)
        for ent in doc.ents:
            if ent.kb_id_ not in dbDic.values():
                dbDic[ent.text] = ent.kb_id_
                # print(ent.text, ent.label_)

      

        if(len(dbDic)<=len(spacyDic)):
            for str in dbDic:
                # print(str)
                if str in spacyDic:
                    
                    dup['CourseId'].append(courseID)
                    dup['Type'].append(type)
                    dup['Identifier'].append(lectureID)
                    dup['Topic Name'].append(str)
                    dup['Topic Link'].append(dbDic.get(str))
                    dup['Entity Type'].append(spacyDic.get(str))
                    
        else:
            for str in spacyDic:
            
                if str in dbDic:
                    
                    dup['CourseId'].append(courseID)
                    dup['Type'].append(type)
                    dup['Identifier'].append(lectureID)
                    dup['Topic Name'].append(str)
                    dup['Topic Link'].append(dbDic.get(str))
                    dup['Entity Type'].append(spacyDic.get(str))
              


        print("Could not read file:", file)
    file.close()

if __name__ == "__main__":
    path = r"C:\Users\jbdou\Downloads\COMP6741\\"
    IS_worksheet_directory = r"C:\Users\jbdou\Downloads\COMP6741\Lecture"
    IS_lecture_directory = r"C:\Users\jbdou\Downloads\COMP6741\Worksheet"
    
    dup = {
        'CourseId': [],
        'Type': [],
        'Identifier': [],
        'Topic Name': [],
        'Topic Link': [],
        'Entity Type': []
 
    }
    dbDic={}
    spacyDic={}
    pattern=["ORG","MONEY","PERSON","WORK OF ART","LANGUAGE","EVENT","TYPE"]

    count = 1
    for txtfile in os.listdir(IS_lecture_directory):
        print(str(txtfile))
        generate_topics('40355', 'Lecture', count, IS_lecture_directory + '\\' + txtfile)
        count = count + 1


    count = 1
    for txtfile in os.listdir(IS_worksheet_directory):
        print(str(txtfile))
        generate_topics('40355', 'WorkSheet', count, IS_worksheet_directory + '\\' + txtfile)
        count = count + 1

    

    

    df = pd.DataFrame(dup)
    df.to_csv(path+'Topics1.csv', index=False)
 