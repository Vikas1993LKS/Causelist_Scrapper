# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 16:51:14 2020

@author: Vikas Gupta
"""


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import time
from datetime import datetime
import os
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
# from azure.cosmos import CosmosClient, PartitionKey, exceptions
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
download_dir = ""

chrome_options = Options()
options = webdriver.ChromeOptions()
# options.add_experimental_option('prefs', {
# "download.default_directory": download_dir,  # Change default directory for downloads
# "download.prompt_for_download": False,
# "plugins.always_open_pdf_externally": True  # To auto download the file
#  }) 


regexp = re.compile(r'^([0-9]{1,3})$|^([0-9]{1,3}\.[0-9]{1,2})$')
regexp_connected = re.compile(r'([0-9]{1,3}\.[0-9]{1,2})')
today_date = datetime.today().strftime('%d-%m-%Y')
listing_details = re.compile(r'(ORDERS|FOR MOTION HEARING|BAIL APPLICATIONS|SUSPENSION OF SENTENCE|PART HEARD|DEFECT|CONTEMPT OF COURT|FOR APPEARANCE|FOR HEARING|PETITIONS|FOR JUDGEMENT|ADMISSION|INTERLOCUTORY|INTERIM ORDERS|FRESH MATTERS|MOTION HEARING MATTERS|FOR ORDERS|FOR ADMISSION|CONDONATION OF FILING DELAY|FINAL DISPOSAL/FINAL HEARING|FOR DISPOSAL)', re.IGNORECASE)
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
# driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
# params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
# command_result = driver.execute("send_command", params)

# url = os.environ['ACCOUNT_URI']
# key = os.environ['ACCOUNT_KEY']
# client = CosmosClient(url, credential=key)            
# database_name = "causelist"
# container_name = "causelistcontainer"
# database_client = client.get_database_client(database_name)
# container_client = database_client.get_container_client(container_name)

db_name = os.environ['MONGO_DB']
host = os.environ['MONGO_HOST']
port = 10255
username = os.environ['MONGO_USERNAME']
password = os.environ['MONGO_PASSWORD']
args = "ssl=true&retrywrites=false&ssl_cert_reqs=CERT_NONE&connect=false"
connection_uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}?{args}"
client = MongoClient(connection_uri)
db = client[db_name]
user_collection = db['user']


url = "https://mphc.gov.in/causelist"
driver.get(url)
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
Bench = input("Please enter the Bench for Causelist fetch\n")

if (Bench == "Indore"):
    Bench_Selection = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/section/div/div/div/div/div/div/div/div[2]/select/option[2]")
    Bench_Selection.click()
elif (Bench == "Gwalior"):
    Bench_Selection = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/section/div/div/div/div/div/div/div/div[2]/select/option[3]")
    Bench_Selection.click()
elif (Bench == "Jabalpur"):
    Bench_Selection = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/section/div/div/div/div/div/div/div/div[2]/select/option[1]")
    Bench_Selection.click()
    
time.sleep(2)

Judge_Selection = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/section/div/div/div/div/div/div/div/div[3]/div/div[1]/div/form/div/div/table/tbody/tr[3]/td/select/option[2]")

Judge_Selection.click()

# Judge_Names = []

# Count_Judge = 0

# for Judge_Name in driver.find_elements_by_xpath("//*[@id='aw1']/option"):
#     Count_Judge += 1
#     if (Count_Judge > 2):
#         Judge_Names.append(Judge_Name.text)

time.sleep(2)
# 
# Date_Selection = driver.find_element_by_xpath("/html/body/div[3]/div/div/div/section/div/div/div/div/div/div/div/div[3]/div/div[1]/div/form/div/div/table/tbody/tr[4]/td/span[1]/input")

# Date_Selection.click()

# Calendar_Table = driver.find_element_by_xpath("//*[@id='ui-datepicker-div']/table")

# time.sleep(3)

# Month_selector = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]")

# Month_selector.click()

# Date = input("enter the date in dd-mm-yyyy format\n")

# Month_Value = Date.split("-")[1]

# if (Month_Value == "01"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[1]")
#     Month_value.click()
# elif (Month_Value == "02"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[2]")
#     Month_value.click()
# elif (Month_Value == "03"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[3]")
#     Month_value.click()
# elif (Month_Value == "04"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[4]")
#     Month_value.click()
# if (Month_Value == "05"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[5]")
#     Month_value.click()
# elif (Month_Value == "06"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[6]")
#     Month_value.click()
# elif (Month_Value == "07"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[7]")
#     Month_value.click()
# elif (Month_Value == "08"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[8]")
#     Month_value.click()
# if (Month_Value == "Sep"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[9]")
#     Month_value.click()
# elif (Month_Value == "Oct"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[10]")
#     Month_value.click()
# elif (Month_Value == "Nov"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[11]")
#     Month_value.click()
# elif (Month_Value == "Dec"):
#     Month_value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[1]/option[12]")
#     Month_value.click()


# year = Date.split("-")[2]
# Year_Value = driver.find_element_by_xpath("/html/body/div[8]/div/div/select[2]/option[71]")
# Year_Value.click()

# day_table = driver.find_element_by_xpath("/html/body/div[8]/table/tbody")

# day = int(Date.split("-")[0])

# for days_row in day_table.find_elements_by_xpath(".//tr"):
#     for days in days_row.find_elements_by_xpath(".//td"):
#         for day_value in days.find_elements_by_xpath(".//a"):
#             if (day_value.text == str(day)):
#                 print (day_value.text)
#                 day_value.click()

# day_value = driver.find_element_by_xpath("/html/body/div[8]/table/tbody/tr[3]/td[" +str(day)+"]/a")

# day_value.click()

causelist_show_button = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/section/div/div/div/div/div/div/div/div[3]/div/div[1]/div/form/div/div/table/tbody/tr[5]/td/input")

causelist_show_button.click()


#driver.execute_script("document.getElementById('value').checked = true;")

#Date_selection = driver.find_element_by_id("value")

time.sleep(10)

Causelist_Content = driver.find_element_by_xpath("//*[@id='adv_cl_en_wp']")

Case_Regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')

Cases_Data = []

Count = 0

Case_Number = ""

Cases = []

Case_Numbers = []

Party_Names = []

Petitioner_Advocate_Names = []

Respondent_Advocate_Names = []

petitioner_advocate_names_all = []

respondent_advocate_names_all = []

Tentative_dates = []

Party_Name = []
Petitioner_Advocate_Name = []
Respondent_Advocate_Name = []

JSON_Complete_Data = []
table_counter = -1

Judge_Names = []

for judge in Causelist_Content.find_elements_by_xpath(".//div[@align = 'center']"):
    for judge_name in judge.find_elements_by_xpath("//u"):
        if ("JUSTICE" in judge_name.text):
            if (judge_name.text not in Judge_Names):
                Judge_Names.append(judge_name.text)


for table in Causelist_Content.find_elements_by_xpath(".//table[@class = 'mytable']"):
    table_counter+=1
    for row in table.find_elements_by_xpath(".//tr"):
        Case_data = []
        for row_value in row.find_elements_by_xpath(".//td"):
            row_text = row_value.text
            if (listing_details.search(row_text)):
                print (row_text)
                hearing_details_text = row_text.strip()
            if (regexp.search(row_text)):
                serial_number = row_text.strip()
            if (row_text.strip() != ""):
                if (Case_Regex.search(row_text) and not(date_regex.search(row_text)) and Count == 0):
                    Case_Number = row_text
                    Count += 1
                else:
                    Case_data.append(row_text.strip())
                    Count = 0
        if (len(Case_data) != 0):
            if (Case_Number not in Case_Numbers and Case_Number.strip() != "" and "-" in Case_Number):
                Case_Numbers.append(Case_Number)
                JSON_Data = {"case_numbers": Case_Number.replace("\n", "")}
            Case_details = {"Case_Numbers" : Case_Number, "Case_data" : Case_data}
            Cases.append(Case_details)
            if (len(Case_data) == 4) and Case_data[0].lower() != "vs.":
                Party_Name.append(Case_data[1])
                Petitioner_Advocate_Name.append(Case_data[2])
                Tentative_dates.append(Case_data[3])
                tentative_date = Case_data[3]
                JSON_Data["tentative_date"] = Case_data[3]
            elif (len(Case_data) == 3) and "vs." in Case_data[0].lower():
                Party_Name.append(Case_data[0])
                Party_Name.append(Case_data[1])
                Respondent_Advocate_Name.append(Case_data[2])
                Cleaned_Party_Name = " ".join(Party_Name)
                JSON_Data["party_names"] = Cleaned_Party_Name 
                Cleaned_Petitioner_Advocate_Name = " ".join(Petitioner_Advocate_Name)
                for name in Cleaned_Petitioner_Advocate_Name.split(","):
                    advocate_name = {"name": name}
                    petitioner_advocate_names_all.append(advocate_name)
                JSON_Data["petitioner_advocate_names"] = petitioner_advocate_names_all
                Cleaned_Respondent_Advocate_Name = " ".join(Respondent_Advocate_Name)
                for name in Cleaned_Respondent_Advocate_Name.split(","):
                    advocate_name = {"name": name}
                    respondent_advocate_names_all.append(advocate_name)
                JSON_Data["respondent_advocate_names"] = respondent_advocate_names_all
                JSON_Data["advocate_names"] = []
                JSON_Data["addtitional_details"] = ""
                JSON_Data["hearing_details"] = hearing_details_text
                JSON_Data["remarks"] = ""
                Judge_Name_Dict = {"name" : Judge_Names[table_counter]}
                JSON_Data["judge_name"] = Judge_Name_Dict
                JSON_Data["tentative_date"] = tentative_date
                JSON_Data["court_number"] = "" + "S.No. " + serial_number
                JSON_Data["forum"] = "High Court"
                JSON_Data["date"] = today_date
                JSON_Data["state"] = "Madhya Pradesh"
                Cleaned_Tentative_date = " ".join(Tentative_dates)
                Party_Name = []
                Petitioner_Advocate_Name = []
                petitioner_advocate_names_all = []
                Respondent_Advocate_Name = []
                respondent_advocate_names_all = []
                Party_Names.append(Cleaned_Party_Name)
                Petitioner_Advocate_Names.append(Cleaned_Petitioner_Advocate_Name)
                Respondent_Advocate_Names.append(Cleaned_Respondent_Advocate_Name)
                JSON_Complete_Data.append(JSON_Data)
            elif (len(Case_data) == 2) and "vs." in Case_data[0].lower():
                Party_Name.append(Case_data[0])
                Party_Name.append(Case_data[1])
                Cleaned_Party_Name = " ".join(Party_Name)
                JSON_Data["party_names"] = Cleaned_Party_Name 
                Cleaned_Petitioner_Advocate_Name = " ".join(Petitioner_Advocate_Name)
                for name in Cleaned_Petitioner_Advocate_Name.split(","):
                    advocate_name = {"name": name}
                    petitioner_advocate_names_all.append(advocate_name)
                JSON_Data["petitioner_advocate_names"] = petitioner_advocate_names_all
                Cleaned_Respondent_Advocate_Name = " ".join(Respondent_Advocate_Name)
                for name in Cleaned_Respondent_Advocate_Name.split(","):
                    advocate_name = {"name": name}
                    respondent_advocate_names_all.append(advocate_name)
                JSON_Data["respondent_advocate_names"] = respondent_advocate_names_all
                Judge_Name_Dict = {"name" : Judge_Names[table_counter]}
                JSON_Data["respondent_advocate_names"] = respondent_advocate_names_all
                JSON_Data["advocate_names"] = []
                JSON_Data["addtitional_details"] = ""
                JSON_Data["hearing_details"] = hearing_details_text
                JSON_Data["remarks"] = ""
                JSON_Data["judge_name"] = Judge_Name_Dict
                #JSON_Data["tentative_date"] = tentative_date
                JSON_Data["court_number"] = "" + "S.No. " +  serial_number
                JSON_Data["forum"] = "High Court"
                JSON_Data["date"] = today_date
                JSON_Data["state"] = "Madhya Pradesh"
                Cleaned_Tentative_date = " ".join(Tentative_dates)
                Party_Name = []
                Petitioner_Advocate_Name = []
                petitioner_advocate_names_all = []
                Respondent_Advocate_Name = []
                respondent_advocate_names_all = []
                Party_Names.append(Cleaned_Party_Name)
                Petitioner_Advocate_Names.append(Cleaned_Petitioner_Advocate_Name)
                Respondent_Advocate_Names.append(Cleaned_Respondent_Advocate_Name)
                JSON_Complete_Data.append(JSON_Data)

for value in range(len(JSON_Complete_Data)):
    if (regexp_connected.search(JSON_Complete_Data[value]["court_number"])):
        index = value
        for i in range(index, -1, -1):
            if (not(regexp_connected.search(JSON_Complete_Data[i]["court_number"]))):
                associated_case_number = JSON_Complete_Data[i]["case_numbers"]
                remarks = {"remarks": "in association with " + associated_case_number}
                JSON_Complete_Data[value].update(remarks)
                break

# with open("Output.txt", "w") as f:
#     f.write(str(JSON_Complete_Data))
# print (JSON_Complete_Data)                
# for value in JSON_Complete_Data:
#     container_client.upsert_item(value)
for value in JSON_Complete_Data:
    user_collection.insert_one(value)