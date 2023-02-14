import PyPDF2
import re
import os


def format_notes(page_text):
    page_text = page_text.strip()
    replacements = [
        ("\t", " "),
        ("  ", "\n\n"),
        (r"\s+-\s+", "\n- "),
        (r"\s+o\s+", "\n\to "),
        (r"\s+§\s+", "\n\t\t§ "),
        ("\n{3,}", "\n\n"),
        (r"Ian J\. Gerard MDCM 2020\s+\d+", "")
    ]
    for pattern, replacement in replacements:
        page_text = re.sub(pattern, replacement, page_text)
    return page_text


def get_page(n):
    with open('./RRP-Notes.pdf', 'rb') as pdf:
        reader = PyPDF2.PdfReader(pdf)
        return reader.pages[n].extract_text()
    return None


def get_num_pages():
    with open('./RRP-Notes.pdf', 'rb') as pdf:
        return len(PyPDF2.PdfReader(pdf).pages)
    return 0


def get_table_of_contents():
    # ignores section headings since it can't differentiate them
    result = "".join([get_page(n) for n in range(4)])
    replacements = [
        (r"\s+", " "),
        (r"Ian J\. Gerard MDCM 2020\s+\d+", ""),
        (r"\s+Table of Contents\s+", ""),
        (r"\s*\.+\s*(\d+)\s*", r"::\1\n")  # previously the pattern also captured trailing whitespace
    ]
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    result = [x.split("::") for x in result.strip().split("\n")] + [["dummy", str(get_num_pages())]]
    return [[re.sub(r"(/|\s)+", "_", t1), int(n1) - 1, int(n2) - 1] for [t1, n1], [_, n2] in zip(result, result[1:])]


def create_chunks():
    directory = "chunks"
    if not os.path.exists(directory):
        os.makedirs(directory)

    toc = get_table_of_contents()
    # Iterate over each page in the pages list
    for name, start, stop in toc:
        # Create a file to store the chunk
        filename = f"{directory}/{name}.txt"
        with open(filename, "w") as file:
            for i in range(start, stop):
                file.write(format_notes(get_page(i)))
                print("wrote page " + str(i))


create_chunks()
