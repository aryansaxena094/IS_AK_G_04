from tika import parser
import os
def parse_and_save_files(input_directory, output_directory, file_prefix):
    tika.initVM() # type: ignore
    for i, filename in enumerate(os.listdir(input_directory), start=1):
        input_file_path = os.path.join(input_directory, filename)
        output_file_path = os.path.join(output_directory, f'{file_prefix}{i}.txt')
        print(f'Processing file: {filename}')
        parsed = parser.from_file(input_file_path)
        content = parsed.get("content", "").strip()
        lines = list(filter(None, content.split("\n")))
        unique_lines = "\n".join(sorted(set(lines), key=lines.index))
        with open(output_file_path, 'w', encoding='UTF-8') as f_out:
            f_out.write(unique_lines)
if __name__ == "__main__":
    IS_base_directory = "TextConv/COMP6741"
    worksheet_directory = os.path.join(IS_base_directory, "Worksheet")
    lecture_directory = os.path.join(IS_base_directory, "Lecture")
    parse_and_save_files(worksheet_directory, worksheet_directory, 'worksheet')
    parse_and_save_files(lecture_directory, lecture_directory, 'slide')