# Mercedez-Benz Order Guide Extractor
## Extract the text from your PDF
1. Navigate to the project folder and run ```python main.py```
2. Select the proper Order Guide when prompted
3. The data will be saved in a SQLite file or JSON format for your archives
## Insert the data into PCS Maintenance
1. Open PCS Maintenance and manually set your effective date
2. Run ```python insert.py```
3. Select one or more models from the menu
4. Press "Start"