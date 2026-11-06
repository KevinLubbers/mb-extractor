import easygui
import os
import json
import sys
import pyautogui, time, pygetwindow
import pyperclip
import logging

#logging setup
logger = logging.getLogger()

# Set the log level (e.g., INFO level for general logs)
logger.setLevel(logging.INFO)

# Create a file handler that logs to 'input_check_log.txt'
file_handler = logging.FileHandler('pcs_input_log.txt', mode='a')
file_handler.setLevel(logging.INFO)  # Set the file handler's log level

# Create a stream handler to log to the console (stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set the console handler's log level

# Define the log format
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
#end logging setup

def navToPXorAX(response_check):
    if response_check:
        #nav to AX model
        pyautogui.press('down')
        pyautogui.press('down')
    else:
        #nav to PX model
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')

    #navigate to options
    time.sleep(.5)
    pyautogui.press('alt')
    pyautogui.press('s')
    time.sleep(1)
    pyautogui.press('o')
    time.sleep(.5)
    
    time.sleep(2)
    
    
def navCheckPrice():
    pyautogui.press('alt')
    pyautogui.press('s')
    time.sleep(1)
    pyautogui.press('i')
    time.sleep(.5)
    
    time.sleep(1)

def deleteOption():
    pyautogui.press('alt')
    pyautogui.press('p')
    time.sleep(1)
    pyautogui.press('d')
    time.sleep(.5)
    pyautogui.press('enter')
    
    time.sleep(1)
    
def findOptionCategory(json_category):
    case_dict = {
        "INT": "INT",
        "GROUP": "GROUP",
        "INTFT1": "INTFT1",
        "PORT": "IND",
        "IND": "IND",
        "Color": "EXT",
        "Trim": "DECOR",
        "Base Trim": "DECOR",
        "Trim-Color": "EXT",
        "Wheel": "WHEEL",
        "Suspension": "SUSP"
    }
    converted_category = case_dict.get(json_category)
    return converted_category

def addBadOption(code, name, option_type, invoice, msrp):
    presentation_flag = False
    if option_type == "PORT":
        presentation_flag = True
    option_cat = findOptionCategory(option_type)
    pyautogui.press('alt')
    pyautogui.press('p')
    time.sleep(1)
    pyautogui.press('a')
    time.sleep(1)
    pyautogui.write(code, interval=0.1)
    pyautogui.press('tab')
    pyautogui.write(name, interval=0.1)
    pyautogui.press('tab')
    pyautogui.write(option_cat, interval=0.1)
    pyautogui.press('tab')
    pyautogui.write("MFG", interval=0.1)
    if presentation_flag:
        pyautogui.press('tab')
        pyautogui.write("9200", interval=0.1)
    pyautogui.press('enter')
    time.sleep(.5)
    pyautogui.hotkey('alt', 'c')
    time.sleep(1)
    
    #add price record to new option
    pyautogui.press('alt')
    pyautogui.press('s')
    time.sleep(1)
    pyautogui.press('i')
    time.sleep(1)
    pyautogui.press('tab')
    pyautogui.write(invoice, interval=0.1)
    time.sleep(.5)
    pyautogui.press('tab')
    pyautogui.write(msrp, interval=0.1)
    pyautogui.press('enter')
    time.sleep(.5)

def addOption(invoice, msrp, differential=False):
    pyautogui.press('alt')
    pyautogui.press('p')
    time.sleep(1)
    pyautogui.press('a')
    time.sleep(.5)
    pyautogui.press('tab')
    time.sleep(.5)
    pyautogui.write(invoice, interval=0.1)
    time.sleep(.5)
    pyautogui.press('tab')
    pyautogui.write(msrp, interval=0.1)
    if differential == True:
        pyautogui.press('tab')
        pyautogui.press('down')
        pyautogui.press('down')
    pyautogui.press('enter')
    time.sleep(.5)
    
def addPaintsToColorChart(colors):
    #navigate to option description field, cant use option field because use of different option codes
    pyautogui.press('backspace')
    pyautogui.press('tab')
    time.sleep(.5)
    pyautogui.write("EXT", interval=0.1)
    pyautogui.press('f5')
    time.sleep(.5)
    pyautogui.press('alt')
    pyautogui.press('s')
    time.sleep(.5)
    pyautogui.press('g')
    
    #inside color group window - adding colors
    time.sleep(1)
    pyautogui.press('alt')
    pyautogui.press('p')
    time.sleep(1)
    pyautogui.press('a')
    time.sleep(2)
    for color in colors:
        pyautogui.write(color, interval=0.1)
        time.sleep(.5)
        pyautogui.press('enter')
        time.sleep(.5)
        pyautogui.press('enter')
        time.sleep(.5)
    time.sleep(.5)
    pyautogui.hotkey('alt', 'c')
    #pyautogui.press('alt')
    #pyautogui.press('c')
    time.sleep(.5)
    exitScreen()
    time.sleep(.5)
    #delete EXT text to show all options again
    pyautogui.press('backspace')
    pyautogui.press('f5')
    
def exitScreen():
    pyautogui.hotkey('alt', 'f')
    time.sleep(.5)
    pyautogui.press('c')
    time.sleep(.5)


try:
    #MSG Box to select JSON file
    setup_or_proof = easygui.ynbox("Is this a model setup or proof updates?", title="Model Setup or Proof?", choices=["Model Setup", "Proof"])

    file_path = easygui.fileopenbox(title="Select a JSON file", default=os.path.join(os.getcwd(), "*.json"))

    if file_path:
        print(f"Selected file: {file_path}")
    else:
        print("No file selected.")
        os.system("pause")
    
    #useless message to remind user to open PCS
    response = easygui.ynbox("Script will fail if PCS is not Open\nIs PCS Maintenance Open?", title="Open PCS Reminder", choices=["Yes", "No"])
    
    if not response:
        sys.exit("PCS not opened. Please Try Again")
    
    #useful message with choice which effects navigation
    px_response = easygui.ynbox("Are you entering a PX or AX model?\nNOTE: If only 1 instance of the model exists, select AX (regardless of if model is truly AX/PX)", title="PX or AX?", choices=["PX", "AX"])
    
    
    #load in JSON file then loop through models to create a cli menu
    with open(file_path, "r") as file:
        data = json.load(file)
    #need to change for MB, currently we only have model, no name or family
    for i in range(len(data)):
        print(f"{i}.) {data[i]['model']}")

    #model batch selection menu
    selected_models = None
    while selected_models is None:
        choice = input(f"Select the model(s) (0 - {len(data) - 1}), each separated by a space: ")
        indexes = [int(i) for i in choice.split()]
        if not all(0 <= i < len(data) for i in indexes):
            print("Invalid input. Please enter valid indexes.")
            continue
        selected_models = [data[i] for i in indexes]

    print(f"Selected models: {[model.get('model') for model in selected_models]}")
    time.sleep(1)

    #Bring PCS Window to foreground and maximize
    pcs_window = pygetwindow.getWindowsWithTitle('PCS Maintenance')
    pcs_window[0].activate()
    pcs_window[0].maximize()

    for each_model in selected_models:
        #type model code then year then refresh
        pyautogui.write(each_model["model"], interval=0.1)
        pyautogui.press('tab')
        pyautogui.press('tab')
        #change YEAR here
        pyautogui.write("2027", interval=0.1)
        pyautogui.press('f5')
        time.sleep(.5)
        
        #tab over to model grid
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        time.sleep(.5)
        
        #using choice from earlier
        navToPXorAX(px_response)
        
        #used in loop to collect options based on certain conditions
        bad_options = []
        good_options = []
        bad_price = []
        good_price = []
        paint_list = []
        #contains all options for this MY - used to compare against last MY options
        display_list = []
        display_list.append(f"{'Option':<7} {'Type':<15} {'Invoice':<9} {'MSRP':<9} {'Name':<30}")
        #loop through options for current model
        for each_option in each_model["options"]:
            display_text = f"{each_option["option"]:<7} {each_option["type"]:<15} {each_option["invoice"]:<9} {each_option["msrp"]:<9} {each_option["name"]:<30}"
            display_list.append(display_text)
            if each_option["type"] == "Color" or each_option["type"] == "Trim-Color":
                paint_list.append(each_option["option"])

            #grab list of "old" options from PCS and compare to new options
            for _ in range(7):
                pyautogui.press('tab')
            time.sleep(.5)
            pyautogui.press('right')
            pyautogui.keyDown('shift')
            pyautogui.press('right')
            pyautogui.press('pagedown')
            pyautogui.press('pagedown')
            pyautogui.press('pagedown')
            pyautogui.press('pagedown')
            pyautogui.keyUp('shift')
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(2)
            copy_options = pyperclip.paste().strip()
            lookup = []
            #separate the code and name from the clipboard data
            for line in copy_options.splitlines():
                code, name = line.split(maxsplit=1)
                lookup.append((code, name))
            #return to option input field
            for _ in range(7):
                pyautogui.hotkey('shift', 'tab')
            time.sleep(.5)
            #end grabbing of "old" PCS options

            #write option code then check if it exists in PCS
            #add to bad options if doesnt exist
            pyautogui.write(each_option["option"], interval=0.1)
            pyautogui.press('f5')
            time.sleep(1)
            pyautogui.press('tab')
            pyautogui.press('tab')
            pyautogui.press('tab')
            pyautogui.press('tab')
            pyautogui.press('tab')
            pyautogui.press('tab')
            pyautogui.press('tab')
            pyautogui.press('down')
            pyautogui.press('right')
            time.sleep(.5)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)
            copy_check = pyperclip.paste().strip()
            if not copy_check == each_option["option"]:
                bad_options.append(each_option)
                addBadOption(each_option["option"], each_option["name"], each_option["type"], each_option["invoice"], each_option["msrp"])
            else:
                good_options.append(each_option)
                navCheckPrice()
                #nav to invoice then copy
                pyautogui.press('right')
                pyautogui.press('right')
                pyautogui.press('right')
                pyautogui.press('right')
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(1)
                invoice_check = pyperclip.paste().strip()
                if not float(invoice_check) == float(each_option["invoice"]):
                    #check if another *MDL option(we don't want to delete base price)
                    if not each_option["type"] == "Differential":
                        if setup_or_proof:
                            deleteOption()
                        #add to bad price list and delete record
                        bad_price.append(each_option)
                        addOption(each_option["invoice"], each_option["msrp"])
                    else:
                        addOption(each_option["invoice"], each_option["msrp"], True)
                else:
                    #nav to msrp then copy
                    pyautogui.press('right')
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(1)
                    msrp_check = pyperclip.paste().strip()
                    if not float(msrp_check) == float(each_option["msrp"]):
                        if setup_or_proof:
                            deleteOption()
                        #add to bad price list and delete record
                        bad_price.append(each_option)
                        addOption(each_option["invoice"], each_option["msrp"])
                    else:
                        good_price.append(each_option)
                
                #back out of pricing screen with good price present in PCS
                time.sleep(1)
                exitScreen()
            
            #return navigation to Option Field
            pyautogui.hotkey('shift', 'tab')
            pyautogui.hotkey('shift', 'tab')
            pyautogui.hotkey('shift', 'tab')
            pyautogui.hotkey('shift', 'tab')
            pyautogui.hotkey('shift', 'tab')
            pyautogui.hotkey('shift', 'tab')
            pyautogui.hotkey('shift', 'tab')
        
        
        #options loop end - allow user to clean up old codes
        addPaintsToColorChart(paint_list)
        display_list = "\n".join(display_list)
        easygui.msgbox(
            msg="New Options:\n" + display_list,
            title="Delete Old Options"
        )
        
        #Log Info 
        logger.info(f"Model: {each_model["model"]} - {each_model["name"]}")
        logger.info(f"Bad Options: {bad_options}")
        logger.info(f"Good Options with Bad Prices: {bad_price}")
        logger.info(f"Good Options with Good Prices: {good_price}")
        #make sure PCS is focused before backing out of options screen
        #then back out
        pcs_window[0].activate()
        exitScreen()
        
        #return to model code input box(undo initial tabs)
        pyautogui.hotkey('shift', 'tab')
        pyautogui.hotkey('shift', 'tab')
        pyautogui.hotkey('shift', 'tab')
        pyautogui.hotkey('shift', 'tab')
        pyautogui.hotkey('shift', 'tab')
        pyautogui.hotkey('shift', 'tab')
        time.sleep(.5)
        
    #model loop end
    
except Exception as e:
    print(f"An error occurred: {e}")
            
            
os.system("pause") 