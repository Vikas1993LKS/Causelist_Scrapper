# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 15:18:38 2020

@author: Vikas.gupta
"""

import json
import re
import pandas as pd
import os
import sys
from datetime import datetime
sys.path.append(r'D:\Scrapping\Scrapping\Causelist_Project')
# from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pymongo import MongoClient
from Causelist_Metadata.Causelist_Metadata_Extraction import metadata_extractor
listing_details = re.compile(r'(ADMISSION|ADJOURNED|OSA CASES|TO CONDONE DELAY|CMA - MATRIMONIAL CASES|TO GRANT LEAVE|INTERLOCUTORY|INTERIM ORDERS|FRESH MATTERS|MOTION HEARING MATTERS|FOR ORDERS|FOR ADMISSION|FOR JUDGMENT|TO DISPENSE WITH|FINAL DISPOSAL/FINAL HEARING)', re.IGNORECASE)


regexp = re.compile(r'^([0-9]{1,2})')
today_date = datetime.today().strftime('%d.%m.%Y')
Case_Regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
case_regex_2nd = re.compile(r'^([0-9](\))).+?(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')

def parsepdf(data, download_dir):
        Hearing_Types = []
        Hearing_Type = []
        Case_Numbers = []
        Batches = []
        JSON_Complete_Data = []
        db_name = os.getenv("MONGO_DB")
        host = os.getenv("MONGO_HOST")
        port = 10255
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")
        args = "ssl=true&retrywrites=false&ssl_cert_reqs=CERT_NONE&connect=false"
        connection_uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}?{args}"
        client = MongoClient(connection_uri)
        db = client[db_name]
        user_collection = db['user']
        for index in range(len(data)):
            if ("bold" in data[index]['Line_Data']['font_name'].lower() and data[index]['Line_Data']['font_size'] > 10 and data[index]['Line_Data']['leftpoint_x'] > 230 and listing_details.search(data[index]['Line_Data']['Value'])):
                #print (data[index]['Line_Data']['Value'])
                if (data[index] not in Hearing_Type):
                    data[index]['Index'] = index
                    Hearing_Type.append(data[index])
        for value in range(len(data)):
            if (Case_Regex.search(data[value]["Line_Data"]["Value"].strip()) and not(date_regex.search(data[value]["Line_Data"]["Value"])) and len(data[value]["Line_Data"]["Value"]) < 20 and data[value]['Line_Data']['leftpoint_x'] < 100):
                if (regexp.search(data[value-1]["Line_Data"]["Value"]) or case_regex_2nd.search(data[value]["Line_Data"]["Value"])):
                    Case_Details = {"Value" : data[value]['Line_Data']['Value'].replace("\n", ""), "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                else:
                    Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                Case_Numbers.append(Case_Details)
        for values in range(len(Case_Numbers)):
            if (values < len(Case_Numbers) -1):
                Index_1 = Case_Numbers[values]['Index']
                Index_2 = Case_Numbers[values+1]['Index']
                batch = []
                Batch = []
                #Adv_Name = []
                Case_Numb = []
                Datelist = []
                Left_point = 0
                Cleaned_Respondent_Advocate_Names = ""
                for index in range(len(data)):
                    if (index >= Index_1 and index < Index_2):
                        if (Case_Regex.search(data[index]['Line_Data']['Value']) and not(date_regex.search(data[index]["Line_Data"]["Value"])) and len(data[index]["Line_Data"]["Value"]) < 30 and (regexp.search(data[index-1]["Line_Data"]["Value"]))) or (not(date_regex.search(data[index]["Line_Data"]["Value"])) and case_regex_2nd.search(data[index]["Line_Data"]["Value"])):
                            Case_Numb.append(data[index]['Line_Data']['Value'].strip() + "Main Case")
                        elif Case_Regex.search(data[index]['Line_Data']['Value']) and not(date_regex.search(data[index]["Line_Data"]["Value"])) and len(data[index]["Line_Data"]["Value"]) < 30:
                            Case_Numb.append(data[index]['Line_Data']['Value'].strip())
                        else:
                            pass
                    if (index > Index_1 and index < Index_2) and "condone" not in data[index]['Line_Data']['Value'].lower() and "days" not in data[index]['Line_Data']['Value'].lower() and "VKJNGT+CourierNew,Bold" not in data[index]['Line_Data']['font_name'] and len(data[index]['Line_Data']['Value']) < 70 and not(date_regex.search(data[index]['Line_Data']['Value'])) and data[index]['Line_Data']['leftpoint_x'] > 80 and data[index]['Line_Data']['leftpoint_x'] > 100 and "HON'BLE" not in data[index]['Line_Data']['Value'] and "file" not in data[index]['Line_Data']['Value'] and "admission" not in data[index]['Line_Data']['Value'].lower() and "hearing" not in data[index]['Line_Data']['Value'].lower() and "order" not in data[index]['Line_Data']['Value'].lower() and "part" not in data[index]['Line_Data']['Value'].lower() and " pm" not in data[index]['Line_Data']['Value'].lower():
                        batch.append(data[index])
                    else:
                        continue
                Batch = sorted(batch, key=
                                       lambda x: (round(x['Line_Data']['leftpoint_x'], 0)))
                Count = 0
                New_Batch = []
                left_coordinates = []
                coordinates = []
                for value in Batch:
                    left_coordinates.append(value["Line_Data"]["leftpoint_x"])    
                coordinates = sorted(set([i for i in left_coordinates if left_coordinates.count(i)>1]))
                Batches.append(Batch)
                Party_Name = []
                Advocate_Names = []
                for ind in range(len(Batch)):
                    if (ind < len(Batch) -1):
                        if (Count == 0):
                            if (Batch[ind]['Line_Data']['leftpoint_x'] > 100 and Batch[ind]['Line_Data']['leftpoint_x'] in coordinates and Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']):
                                Party_Name.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x'] 
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['leftpoint_x'] > 100 and Batch[ind]['Line_Data']['leftpoint_x'] in coordinates and Batch[ind]['Line_Data']['Value'] not in Party_Name and Batch[ind]['Line_Data']['leftpoint_x'] == Left_point and Left_point != 0):
                                    Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                elif (Batch[ind]['Line_Data']['leftpoint_x'] in coordinates):
                                    Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                        elif (Count == 1):
                            if ((Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x'])):
                                Advocate_Names.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['Value'] not in Advocate_Names) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 300:
                                        Advocate_Names.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                else:
                                    pass
                    elif (ind == len(Batch) - 1) and 200 > Batch[ind]['Line_Data']['leftpoint_x'] > 130:
                        Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 250:
                        Advocate_Names.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                Cleaned_Case_Numbers = ", ".join(Case_Numb).replace("\n", "")
                Cleaned_Party = " ".join(Party_Name).replace("\n", "")
                Cleaned_Advocate_Names = ", ".join(Advocate_Names).replace("\n", "")
                if ("------------------") in Cleaned_Advocate_Names:
                    Cleaned_Petitioner_Advocate_Names = Cleaned_Advocate_Names.split("------------------,")[0]
                    try:
                        if (Cleaned_Advocate_Names.split("------------------,")[1].strip() != ""):
                            Cleaned_Respondent_Advocate_Names = Cleaned_Advocate_Names.split("------------------,")[1]
                    except:
                        pass
                else:
                    Cleaned_Petitioner_Advocate_Names = Cleaned_Advocate_Names
                petitioner_advocate_name_all = []
                respondent_advocate_name_all = []
                for name in Cleaned_Petitioner_Advocate_Names.split(","):
                    if name.strip() != "" and "------------------" not in name.strip():
                        advocate_name = {"name" : name}
                        petitioner_advocate_name_all.append(advocate_name)
                for name in Cleaned_Respondent_Advocate_Names.split(","):
                    if name.strip() != "" and "------------------" not in name.strip():
                        advocate_name = {"name" : name}
                        respondent_advocate_name_all.append(advocate_name)
                #print (Cleaned_Party.replace("\n", ""))
                if (Cleaned_Party.strip() != ""):
                    JSON_Data = {"case_number" : Cleaned_Case_Numbers, "party_names": Cleaned_Party, "petitioner_advocate_names": petitioner_advocate_name_all, "respondent_advocate_names" : respondent_advocate_name_all}
                else:
                    pass
                JSON_Data["advocate_names"] = []
                JSON_Data["additional_details"] = []
                for Hearing in range(len(Hearing_Type)):
                    if (Hearing < len(Hearing_Type) -1):
                        if (Hearing_Type[Hearing+1]['Index'] > Case_Numbers[values]['Index'] > Hearing_Type[Hearing]['Index']):
                            Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())                                
                            JSON_Data["hearing_details"] = Hearing_Type[Hearing]['Line_Data']['Value'].strip()
                        else:
                            Hearing+=1
                    else:
                        if (Case_Numbers[values]['Index'] > Hearing_Type[Hearing]['Index']):
                            Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())
                            JSON_Data["hearing_details"] = Hearing_Type[Hearing]['Line_Data']['Value'].strip()
                JSON_Data["remarks"] = ""
                Judge_Name = metadata_extractor(data)[0]
                Court_Numbers = metadata_extractor(data)[1]
                for Judge in range(len(Judge_Name)):
                    if (Judge < len(Judge_Name) -1):
                        if (Judge_Name[Judge+1]['Index'] > Case_Numbers[values]['Index'] > Judge_Name[Judge]['Index']):
                            judge_name_all = []
                            for name in Judge_Name[Judge]['judge_name']:
                                judge_name = {"name": name.replace("\n", "")}
                                judge_name_all.append(judge_name)
                            JSON_Data["judge_name"] = judge_name_all
                        else:
                            Judge+=1
                    else:
                        if (Case_Numbers[values]['Index'] > Judge_Name[Judge]['Index']):
                            judge_name_all = []
                            for name in Judge_Name[Judge]['judge_name']:
                                judge_name = {"name": name.replace("\n", "")}
                                judge_name_all.append(judge_name)
                            JSON_Data["judge_name"] = judge_name_all
                JSON_Data["tentative_date"] = ""
                for Court in range(len(Court_Numbers)):
                    if (Court < len(Court_Numbers) -1):
                        if (Court_Numbers[Court+1]['Index'] > Case_Numbers[values]['Index'] > Court_Numbers[Court]['Index']):
                            JSON_Data["court_number"] = Court_Numbers[Court]['court_number'].strip()
                        else:
                            Court+=1
                    else:
                        if (Case_Numbers[values]['Index']
                            > Court_Numbers[Court]['Index']):
                            JSON_Data["court_number"] = Court_Numbers[Court]['court_number'].strip()
                        else:
                            JSON_Data["court_number"] = ""
                JSON_Data["forum"] = "High Court"
                JSON_Data["date"] = today_date
                JSON_Data["state"] = "Madras"
                Batches.append(Batch)
                JSON_Complete_Data.append(JSON_Data)
        with open("Input.txt", "w") as f:
            f.write(str(data))
        Counter = 0
        for value in range(len(JSON_Complete_Data)):
            if (value < len(JSON_Complete_Data)-1):
                if (JSON_Complete_Data[value]["judge_name"] == JSON_Complete_Data[value+1]["judge_name"]):
                    Counter += 1
                    Serial_Number = "S.No. " + str(Counter)
                    Court_Number = {"court_number" : JSON_Data["court_number"] + ", " + Serial_Number}
                    #JSON_Data["court_number"] = JSON_Data["court_number"] + " " + Serial_Number
                    JSON_Complete_Data[value].update(Court_Number)
                    Serial_Number = ""
                else:
                    Counter = 0
            else:
                Court_Number = {"court_number" : JSON_Data["court_number"] + ", S.No. " + str(len(JSON_Complete_Data))}
                JSON_Complete_Data[value].update(Court_Number)
        for value in range(len(JSON_Complete_Data)):
            if ("Main Case" not in JSON_Complete_Data[value]["case_number"]):
                index = value
                for i in range(value, -1, -1):
                    if ("Main Case" in JSON_Complete_Data[i]["case_number"]):
                        associated_case_number = JSON_Complete_Data[i]["case_number"]
                        remarks = {"remarks": "in association with " + associated_case_number.replace("Main Case", "")}
                        JSON_Complete_Data[value].update(remarks)
                        break
        for value in range(len(JSON_Complete_Data)):
            case_number = {"case_number" : re.sub(r"regexp", "", JSON_Complete_Data[value]["case_number"]).replace("Main Case", "")}
            JSON_Complete_Data[value].update(case_number)
        # with open("Output.txt", "w") as f:
        #     f.write(str(JSON_Complete_Data))
        # with open("Batches.txt", "w") as f:
        #     for value in Case_Numbers:
        #         f.write(str(value))
        for value in JSON_Complete_Data:
            if (value["party_names"].strip() != ""):
                try:
                    user_collection.insert_one(value)
                except:
                    pass
            
# list1 = []

# def jsonread(pathofjson):
#     for dirpath, dirname, filenames in os.walk(pathofjson):
#         for file in filenames:
#             try:
#                 if file.lower().endswith(".json"):
#                     path = os.path.abspath(os.path.join(dirpath, file))
#                     list1.append(path)
#                 else:
#                     continue
#             except (FileNotFoundError, IOError):
#                 print("runtime exception")

# locationofjson = input("Please enter the location of input pdf :\n")
# outputlocation = input("Please enter the location of output JSON :\n")
# jsonread(locationofjson)
# parsepdf(list1)