# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 14:15:55 2020

@author: Vikas Gupta
"""


import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import re
from azure.cosmos import CosmosClient, PartitionKey, exceptions

today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)

chrome_options = Options()
download_dir = r"D:\Scrapping\HP"
try:
    os.makedirs(download_dir)
except:
    pass

options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {
"download.default_directory": download_dir,  # Change default directory for downloads
"download.prompt_for_download": False,
'protocol_handler.excluded_schemes.tel': False,
"plugins.always_open_pdf_externally": True  # To auto download the file
}) 

chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
command_result = driver.execute("send_command", params)

page_number_rejection = re.compile(r'^([0-9]{1,2})(\/)([0-9]{1,2})$|^([0-9]{1,3})$|(Advocate)$|(Petitioner(\s+)?\/(\s+)?Respondent)$')

URL = "https://highcourt.hp.gov.in/cmis/websitephps1/netbd.php"

driver.get(URL)

go_button_click = driver.find_element_by_xpath("/html/body/form/table[3]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr/td[3]/input")

go_button_click.click()

entire_clause_list_click = driver.find_element_by_xpath(".//input[@value = '  Entire Cause List  ']")

entire_clause_list_click.click()

driver.switch_to.alert.accept()

table_element = driver.find_element_by_xpath("/html/body/div/table/tbody/tr/td/table/tbody")

Case_Number_Beginning = re.compile(r'^(\d{1,3}\.)')

Second_row_beginning = re.compile(r'(\[(Civil|Criminal)\])')

Whole_data = []

Batches_data_dictionary = []

Whole_data_dict = []

Counters = []

Counter = 0

for row in table_element.find_elements_by_xpath(".//tr"):
    Counter += 1
    row_text = row.text
    Case_data =  {"Case_data" : row_text, "index": Counter}
    Whole_data_dict.append(Case_data)
    if (Case_Number_Beginning.search(row_text)):
        # Case_Number_row_data = row_text.split("    ")
        # index = Counter
        # #Case_Number_row_data = list(filter(None, Case_Number_row_data))
        # Case_Number_row_data = [x.strip() for x in Case_Number_row_data if x]
        # #print (Case_Number_row_data)
        Counters.append(Counter)

case_index = 0
Batches = []

def batchprocessor(batch):
    Party = []
    Petitioner_advocate = []
    Respondent_advocate = []
    Case_Type = ""
    JSON_Complete_Data = []
    url = os.environ['ACCOUNT_URI']
    key = os.environ['ACCOUNT_KEY']
    client = CosmosClient(url, credential=key)            
    database_name = "causelist"
    container_name = "causelistcontainer"
    database_client = client.get_database_client(database_name)
    container_client = database_client.get_container_client(container_name)
    for value in range(len(batch)):
        advocate_names_all_petitioner = []
        advocate_names_all_respondent = []
        Space_count = []
        if (value < 5):
            # print (batch[value]['Case_data'])
            # list1 = [x.strip() for x in batch[value]['Case_data'].split("   ") if x]
            for spaces in re.findall("(\s+)", batch[value]['Case_data']):
                    if (len(spaces) > 3):
                        Space_count.append(len(spaces))
            if (len(Space_count) == 4):
                list1 = [x.strip() for x in batch[value]['Case_data'].split("   ") if x]
                if (len(list1) == 5):
                    Serial_Number = list1[0]
                    Case_Number = list1[1]
                    Party.append(list1[2])
                    Petitioner_advocate.append(list1[3])
                    Respondent_advocate.append(list1[4])
                elif (len(list1) == 4):
                    Case_Type = list1[0]
                    Party.append(list1[1])
                    Petitioner_advocate.append(list1[2])
                    Respondent_advocate.append(list1[3])
            elif (len(Space_count) == 3):
                list1 = [x.strip() for x in batch[value]['Case_data'].split("   ") if x]
                if (len(list1) == 4) and Case_Number_Beginning.search(list1[0]):
                    Serial_Number = list1[0]
                    Case_Number = list1[1]                
                    Party.append(list1[2])
                    if (Space_count[2] < 45):
                        Petitioner_advocate.append(list1[3])
                    else:
                        Respondent_advocate.append(list1[4])
            elif (len(Space_count) == 2):
                list1 = [x.strip() for x in batch[value]['Case_data'].split("   ") if x]
                if (Space_count[0]) <= 11:
                    Case_Type = list1[0]
                elif (11 < Space_count[0]) < 45:
                    Party.append(list1[0])
                if (11 < Space_count[1] < 45):
                    Party.append(list1[1])
                elif (45 < Space_count[1] < 55):
                    Petitioner_advocate.append(list1[1])
                elif (Space_count[1] > 50):
                    Respondent_advocate.append(list1[1])
            elif (len(Space_count) == 1) and ("with" not in batch[value]['Case_data'].lower() and ("in" not in batch[value]['Case_data'].lower())):
                list1 = [x.strip() for x in batch[value]['Case_data'].split("   ") if x]
                if (Space_count[0]) <=11:
                    Case_Type = list1[0]
                elif (11 < Space_count[0] < 45 or "versus" in list1[0].lower()):
                    Party.append(list1[0])
                elif (45 < Space_count[0] < 55):
                    Petitioner_advocate.append(list1[0])
                elif (Space_count[0] > 55):
                    Respondent_advocate.append(list1[0])
    Cleaned_Party = " ".join(Party)
    Cleaned_Petitioner_advocate = ", ".join(Petitioner_advocate)
    Cleaned_Respondent_advocate = ", ".join(Respondent_advocate)
    JSON_Data = {"case_number" : Case_Number, "case_type": Case_Type.replace("[","").replace("]",""), "party_names": Cleaned_Party}
    for name in Cleaned_Petitioner_advocate.split(","):
        advocate_name = {"name": name}
        advocate_names_all_petitioner.append(advocate_name)
    JSON_Data["petitioner_advocate_names"] = advocate_names_all_petitioner
    for name in Cleaned_Respondent_advocate.split(","):
        advocate_name = {"name": name}
        advocate_names_all_respondent.append(advocate_name)
    JSON_Data["respondent_advocate_names"] = advocate_names_all_respondent
    JSON_Data["state"] = "Himachal Pradesh"
    JSON_Complete_Data.append(JSON_Data)
    # print (JSON_Complete_Data)
    for value in JSON_Complete_Data:
        container_client.upsert_item(value)    
    
for index in range(len(Counters) - 1):
    batch = []
    for value in Whole_data_dict:
            if value['index'] >= Counters[index] and value['index'] < Counters[index + 1] and "page" not in value['Case_data'].lower() and not(page_number_rejection.search(value['Case_data'])):
                batch.append(value)
    if (len(batch) != 0):
        batchprocessor(batch)



        