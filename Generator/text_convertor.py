import os
from tika import parser
from pathlib import Path

base_dir = Path.cwd()
base_dir = base_dir / "Generator/"

def init_tika_vm():
    from tika import initVM
    initVM()

def clean_text(raw_text):
    """Remove blank lines and duplicate lines from the text."""
    lines = raw_text.strip().split("\n")
    unique_lines = set()
    cleaned_text = ""
    for line in lines:
        stripped_line = line.strip()
        if stripped_line and stripped_line not in unique_lines:
            cleaned_text += stripped_line + "\n"
            unique_lines.add(stripped_line)
    return cleaned_text

def process_pdf_files(directory_path, output_directory):
    directory_path = Path(directory_path)
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists

    for i, file_path in enumerate(directory_path.iterdir(), start=1):
        if file_path.suffix.lower() == '.pdf':
            try:
                parsed = parser.from_file(str(file_path))
                content = parsed["content"]
                if content:
                    cleaned_content = clean_text(content)
                    output_file_path = output_directory / f'{file_path.stem}.txt'
                    with open(output_file_path, 'w', encoding='UTF-8') as f:
                        f.write(cleaned_content)
                    print(f"Processed {file_path.name} to {output_file_path.name}")
            except Exception as e:
                print(f"Failed to process {file_path.name}: {e}")

if __name__ == "__main__":
    init_tika_vm()
    # Define directories
    worksheet_directory = "/Users/aryansaxena/Desktop/Intelligent Systems/2-WORKSHEETS"
    lecture_directory = "/Users/aryansaxena/Desktop/Intelligent Systems/1-SLIDES"
    save_worksheet_directory = base_dir / "COMP6741/Worksheet"
    save_lecture_directory = base_dir / "COMP6741/Lecture"

    # Process PDFs
    process_pdf_files(worksheet_directory, save_worksheet_directory)
    process_pdf_files(lecture_directory, save_lecture_directory)
