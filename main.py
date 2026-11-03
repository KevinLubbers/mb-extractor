import easygui
import pymupdf
import re
import json

file_path = easygui.fileopenbox(title="Select the Mercedes-Benz PDF to Convert", filetypes=["*.pdf"])
file_name = file_path.split("\\")[-1]
whole_text = ""
if file_path:
    #open file and extract text from each page
    with pymupdf.open(file_path) as pdf:
# Loop through each page
        for page_number in range(pdf.page_count):
            page = pdf.load_page(page_number)
            
            # Extract text from the page
            page_text = page.get_text("text")
            whole_text += page_text

    #print(whole_text)
    model_and_price_pattern = re.compile(r"\w+\d{3}\w*\s\(\d+\.\d+\)\n.MSRP:\s\$\d{2,3},\d{3}")
    model_and_prices = model_and_price_pattern.findall(whole_text)

    model_code_pattern = re.compile(r"\w+\d{3}\w*")
    model_price_pattern = re.compile(r"\$\d{2,3},\d{3}")

    model_list= []
    option_list = []
    for each_match in model_and_prices:
        model_price = model_price_pattern.findall(each_match)
        model_code = model_code_pattern.findall(each_match)

        model_price = model_price[0].replace(",", "")
        model_price = model_price.replace("$", "")
        model_list.append({"model": model_code[0], "options": [{"option": "*MDL", "name": "Base Price", "invoice": (int(model_price) * .8), "msrp": model_price}]})


    paint_pattern = re.compile(r"^\w{3}\n(?:.*\n)?.*\n.*\n\$\d+,?\d*", flags=re.MULTILINE)
    paints = paint_pattern.findall(whole_text)

    packages_pattern = re.compile(r"^D\w{2}\n(?:.*\n){2,25}\$\d+,?\d*|P\w{2}\n(?:.*\n){2,25}\$\d+,?\d*", flags=re.MULTILINE)
    packages = packages_pattern.findall(whole_text)

    for each_paint in paints:
        each_paint = each_paint.split("\n")
        option_code = each_paint[0]
        option_name = each_paint[1]
        option_msrp = each_paint[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        option_list.append({"option": option_code, "name": option_name, "invoice": (int(option_msrp) * .8), "msrp": option_msrp})

    for each_package in packages:
        each_package = each_package.split("\n")
        option_code = each_package[0]
        option_name = each_package[1]
        option_msrp = each_package[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        option_list.append({"option": option_code, "name": option_name, "invoice": (int(option_msrp) * .8), "msrp": option_msrp})

    for each_model in model_list:
        for each_option in option_list:
            each_model["options"].append(each_option)
    print(json.dumps(model_list, indent=4))