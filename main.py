import easygui
import pdfplumber

file_path = easygui.fileopenbox(title="Select the Mercedes-Benz PDF to Convert", filetypes=["*.pdf"])
file_name = file_path.split("\\")[-1]
whole_text = ""
if file_path:
    #open file and extract text from each page
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            whole_text += text
            tables = page.extract_tables()
            for table in tables:
                print(table)

        choice = input("Press enter to see the whole text unstructured")

        print(whole_text)