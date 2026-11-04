import easygui
import pymupdf
import re
from openpyxl import Workbook
from openpyxl.styles import Font


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

    #start RegEx pattern matching

    #get model codes and pricing
    model_and_price_pattern = re.compile(r"\w+\d{3}\w*\s\(\d+\.\d+\)\n.MSRP:\s\$\d{2,3},\d{3}")
    model_and_prices = model_and_price_pattern.findall(whole_text)

    model_code_pattern = re.compile(r"\w+\d{3}\w*")
    model_price_pattern = re.compile(r"\$\d{2,3},\d{3}")

    model_list= []
    option_list = []
    seen_options = set()
    rear_string = ""
    for each_match in model_and_prices:
        model_price = model_price_pattern.findall(each_match)
        model_code = model_code_pattern.findall(each_match)

        model_price = model_price[0].replace(",", "")
        model_price = model_price.replace("$", "")
        model_list.append({"model": model_code[0], "options": [{"option": "*MDL", "name": "Base Price", "invoice": (int(model_price) * .8), "msrp": model_price}]})

    #start text patterns
    paint_text_pattern = re.compile(r"Paint\n(?:(?!Wheels).*\n)*Wheels\n")
    paint_text = paint_text_pattern.findall(whole_text)

    wheel_text_pattern = re.compile(r"^Wheels\n^\w{3}\s-\s.*\n(?:(?!Upholstery).*\n)*Upholstery\n", flags=re.MULTILINE)
    wheel_text = wheel_text_pattern.findall(whole_text)

    upholstery_text_pattern = re.compile(r"^Upholstery\n(?:(?!Trims).*\n)*Trims\n", flags=re.MULTILINE)
    upholstery_text = upholstery_text_pattern.findall(whole_text)

    trim_text_pattern = re.compile(r"^Trims\n(?:(?!Packages).*\n)*Packages\n", flags=re.MULTILINE)
    trim_text = trim_text_pattern.findall(whole_text)

    packages_text_pattern = re.compile(r"Packages\nAvailability\n(?:(?!VPC Installed Options).*\n)*VPC Installed Options\n|Packages\nAvailability\n(?:(?!VPC-Installed Accessories).*\n)*VPC-Installed Accessories\n", flags=re.MULTILINE)
    packages_text = packages_text_pattern.findall(whole_text)

    port_installed_pattern = re.compile(r"^VPC Installed Options\n(?:(?!^Factory Options\n|^Specifications\n).*\n)*^Factory Options\n|^VPC Installed Options\n(?:(?!^Specifications\n|^Factory Options\n).*\n)*^Specifications\n|^VPC-Installed Accessories\n(?:(?!^Specifications\n|^Factory Options\n).*\n)*^Specifications\n|^VPC-Installed Accessories\n(?:(?!^Factory Options\n|^Specifications\n).*\n)*^Factory Options\n", flags=re.MULTILINE)
    port_installed_text = port_installed_pattern.findall(whole_text)

    factory_options_pattern = re.compile(r"Factory Options\n(?:(?!Specifications).*\n)*Specifications\n|Factory Options\n(?:(?!VPC Installed Options).*\n)*VPC Installed Options\n")
    factory_options_text = factory_options_pattern.findall(whole_text)
    #end text patterns

    #RegEx patterns for each different type of option / display
    options_pattern = re.compile(r"^\w{3}\n(?:\(New\)\n)?(?:.*\n)?.*\n.*\n\$\d+,?\d*", flags=re.MULTILINE)
    factory_options = options_pattern.findall(factory_options_text[0])
    port_installed_options = options_pattern.findall(port_installed_text[0])
    trim_options = options_pattern.findall(trim_text[0])
    upholstery_options = options_pattern.findall(upholstery_text[0])
    paint_options = options_pattern.findall(paint_text[0])

    combo_packages = re.compile(r"^[DP]\w{2}\n(?:(?!\$).*\n){1,25}\$\d+,?\d*", flags=re.MULTILINE)
    c_packages = combo_packages.findall(packages_text[0])


    wheels_pattern = re.compile(r"^\w{3}\n(?:\(New\)\n)?\d{2}\"(?:\/\d{2}\")?\n(?:(?!\$).*\n)+\$\d+,?\d*", flags=re.MULTILINE)
    wheels = wheels_pattern.findall(wheel_text[0])
    #wheel_names = re.compile(r"^\w{3}\s-\s.*\n(?:.*\n){1,4}^\w{3},\s\w{3}\n(?:.*\n){2}", flags=re.MULTILINE)
    wheel_names = re.compile(r"^\w{3}\s-\s.*\n(?:.*\n){1}", flags=re.MULTILINE)
    wheel_names = wheel_names.findall(wheel_text[0])
    #end RegEx pattern matching


    #start looping through each patterns matches and transforming them into a proper structure
    #start paint transformations
    for each_paint in paint_options:
        each_paint = each_paint.split("\n")
        option_code = each_paint[0]
        if each_paint[1] == "(New)":
            option_name = each_paint[2]
        else:
            option_name = each_paint[1]
        option_msrp = each_paint[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        if option_code not in seen_options:
            seen_options.add(option_code)
            option_list.append({"option": option_code, "name": option_name, "invoice": (int(option_msrp) * .8), "msrp": option_msrp, "category": "EXT"})
    #end paint transformations

    #start wheel transformations
    wheel_name_list = []
    for each_wheel_name in wheel_names:
        each_wheel_name = each_wheel_name.split("\n")
        wheel_name = each_wheel_name[0]
        wheel_name = wheel_name.split(" - ")

        if len(each_wheel_name[1]) > 3:
            true_wheel_name = wheel_name[1] + " " + each_wheel_name[1]
        else:
            true_wheel_name = wheel_name[1]

        wheel_name_list.append(true_wheel_name) 

        #start tire transformations
        """
        tires = each_wheel_name[-4]
        tires = tires.split(", ")
        tires[0] = re.findall(r"")[0]
        if tires[0] not in seen_options:
            seen_options.add(tires[0])
            #due to inconsistenties in the OG's we need to use multiple delimiters on this split
            front_wheel = re.split(r', | and |; ',each_wheel_name[-3])
            if front_wheel[1]:
                rear_string = front_wheel[1]
            front_string = front_wheel[0]
            option_list.append({"option": tires[0], "name": front_string, "invoice": 0, "msrp": 0, "category": "TIRES"})
        if tires[1] not in seen_options:
            seen_options.add(tires[1])
            rear_wheels = each_wheel_name[-2]
            if rear_string:
                rear_wheels = rear_string + " " + rear_wheels
                rear_string = ""
            option_list.append({"option": tires[1], "name": rear_wheels, "invoice": 0, "msrp": 0, "category": "TIRES"})
        """
        #end tire transformations

    #transform and add wheel option
    for each_wheel, name in zip(wheels, wheel_name_list):
        each_wheel = each_wheel.split("\n")
        option_code = each_wheel[0]
        option_name = name
        option_msrp = each_wheel[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        if option_code not in seen_options:
            seen_options.add(option_code)
            option_list.append({"option": option_code, "name": option_name, "invoice": (int(option_msrp) * .8), "msrp": option_msrp, "category": "WHEEL"})
    #end wheel transformations

    #start upholstery transformations
    for each in upholstery_options:
        each = each.split("\n")
        option_code = each[0]
        if each[1] == "(New)":
            option_name = each[2]
        else:
            option_name = each[1]
        option_msrp = each[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        if option_code not in seen_options:
            seen_options.add(option_code)
        if "Headliner" in option_name:
            option_list.append({"option": option_code, "name": option_name, "invoice": (int(option_msrp) * .8), "msrp": option_msrp, "category": "INTFT1"})
        else:
            option_list.append({"option": option_code, "name": option_name + " Interior Trim", "invoice": (int(option_msrp) * .8), "msrp": option_msrp, "category": "INT"})

    #start trim transformations
    for each_trim in trim_options:
        each_trim = each_trim.split("\n")
        option_code = each_trim[0]
        if each_trim[1] == "(New)":
            option_name = each_trim[2]
        else:
            option_name = each_trim[1]
        option_msrp = each_trim[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        if option_code not in seen_options:
            seen_options.add(option_code)
            option_list.append({"option": option_code, "name": option_name, "invoice": (int(option_msrp) * .8), "msrp": option_msrp, "category": "DECOR"})

    #start package transformations
    for each_package in c_packages:
        each_package = each_package.split("\n")
        option_code = each_package[0]
        if each_package[1] == "(New)":
            option_name = each_package[2]
        else:
            option_name = each_package[1]
        option_msrp = each_package[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        if option_code not in seen_options:
            seen_options.add(option_code)
            option_list.append({"option": option_code, "name": option_name, "invoice": (int(option_msrp) * .8), "msrp": option_msrp, "category": "GROUP"})

    #start Port Installed Packages transformations
    for each_port_installed in port_installed_options:
        each_port_installed = each_port_installed.split("\n")
        option_code = each_port_installed[0]
        if each_port_installed[1] == "(New)":
            option_name = each_port_installed[2]
        else:
            option_name = each_port_installed[1]
        option_msrp = each_port_installed[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        if option_code not in seen_options:
            seen_options.add(option_code)
            option_list.append({"option": option_code, "name": option_name + " (Port Installed)", "invoice": (int(option_msrp) * .8), "msrp": option_msrp, "category": "PORT"})

    #start Factory Options transformations
    for each_factory in factory_options:
        each_factory = each_factory.split("\n")
        option_code = each_factory[0]
        if each_factory[1] == "(New)":
            option_name = each_factory[2]
        else:
            option_name = each_factory[1]
        option_msrp = each_factory[-1]
        option_msrp = option_msrp.replace("$", "")
        option_msrp = option_msrp.replace(",", "")
        if option_code not in seen_options:
            seen_options.add(option_code)
            option_list.append({"option": option_code, "name": option_name, "invoice": (int(option_msrp) * .8), "msrp": option_msrp, "category": "IND"})
    #end looping through each patterns matches

    #add the options list to each model
    for each_model in model_list:
        for each_option in option_list:
            each_model["options"].append(each_option)

    #start create Excel file
    wb = Workbook()
    ws = wb.active
    ws.title = "Options"

    # Column headers
    fieldnames = ["model", "option", "name", "invoice", "msrp", "category"]
    ws.append(fieldnames)

    # Loop through models and their options
    for each_model in model_list:
        for each_option in each_model["options"]:
            row = [
                each_model["model"],
                each_option.get("option", ""),
                each_option.get("name", ""),
                each_option.get("invoice", ""),
                each_option.get("msrp", ""),
                each_option.get("category", "")
            ]

            ws.append(row)

    for cell in ws[1]:
        cell.font = Font(bold=True)
    for column in ws.columns:
        max_length = max(
            len(str(cell.value or "")) for cell in column
        )
        ws.column_dimensions[column[0].column_letter].width = max_length + 2
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    # Save Excel file
    wb.save("options.xlsx")
    #end create Excel file