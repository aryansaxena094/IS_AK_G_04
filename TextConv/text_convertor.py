import tika
from tika import parser
import os
tika.initVM()


IS_worksheet_directory = r"C:\Users\jbdou\Downloads\COMP6741\Worksheet"
IS_Save_worksheet_directory = r"C:\Users\jbdou\Downloads\COMP6741\Worksheet"
IS_lecture_directory = r"C:\Users\jbdou\Downloads\COMP6741\Lecture"
IS_Save_lecture_directory = r"C:\Users\jbdou\Downloads\COMP6741\Lecture"

i=1
for file in os.listdir(IS_worksheet_directory):
    print(file)
    parsedfile = parser.from_file(IS_worksheet_directory + "\\" + file)
    f = open(IS_Save_worksheet_directory + '\\worksheet' + str(i) + '.txt', 'w', encoding='UTF-8')
    file_string_with_blank_lines = parsedfile["content"].strip()
    lines = file_string_with_blank_lines.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    file_string_without_empty_lines = ""
    lines_seen = set()
    for line in non_empty_lines:
        if line not in lines_seen: # not a duplicate
            file_string_without_empty_lines += line.strip() + "\n"
            lines_seen.add(line)
    f.write(file_string_without_empty_lines)
    f.close()
    i=i+1

i=1
for file in os.listdir(IS_lecture_directory):
    print(file)
    parsedfile = parser.from_file(IS_lecture_directory + "\\" + file)
    f = open(IS_Save_lecture_directory + '\\slide' + str(i) + '.txt', 'w', encoding='UTF-8')
    file_string_with_blank_lines = parsedfile["content"].strip()
    lines = file_string_with_blank_lines.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    file_string_without_empty_lines = ""
    lines_seen = set()
    for line in non_empty_lines:
        if line not in lines_seen: # not a duplicate
            file_string_without_empty_lines += line.strip() + "\n"
            lines_seen.add(line)
    f.write(file_string_without_empty_lines)
    f.close()
    i=i+1