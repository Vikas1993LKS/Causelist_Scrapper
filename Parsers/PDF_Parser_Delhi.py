# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 14:54:09 2020

@author: Vikas Gupta
"""


import json
import re
import pandas as pd
import os
from datetime import datetime
# from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pymongo import MongoClient
from Causelist_Metadata.Causelist_Metadata_Extraction import metadata_extractor


listing_details = re.compile(r'(SENIOR CITIZEN MATTER|FINALS MATTERS|FINAL MATTERS|PART HEARD|DEFECT|CONTEMPT OF COURT|FOR APPEARANCE|FOR HEARING|PETITIONS|FOR JUDGEMENT|ADMISSION|INTERLOCUTORY|INTERIM ORDERS|FRESH MATTERS|MOTION HEARING MATTERS|FOR ORDERS|FOR ADMISSION|CONDONATION OF FILING DELAY|FINAL DISPOSAL/FINAL HEARING|FOR DISPOSAL)', re.IGNORECASE)
today_date = datetime.today().strftime('%d.%m.%Y')
Case_Regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')


def parsepdf(data, download_dir):
            Hearing_Types = []
            Hearing_Type = [] 
            Case_Numbers = []
            Party_Names = []
            Advocate_Names = []
            Index_Numbers = []
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
            # print (user_collection)
            # database_name = "causelist"
            # container_name = "causelistcontainer"
            # database_client = client.get_database_client(database_name)
            # container_client = database_client.get_container_client(container_name)
            #with open(file ,"r") as f:
            #file_name = file.split("\\")[-1]
            #data = json.load(content)
            for index in range(len(data)):
                if (listing_details.search(data[index]['Line_Data']['Value'].strip()) and len(data[index]['Line_Data']['Value'].strip()) < 25):
                    if (data[index] not in Hearing_Type):
                        data[index]['Index'] = index
                        Hearing_Type.append(data[index])
            for value in range(len(data)):
                Line_Index = re.search(r'^([0-9]{0,2}(\.))(.*)((((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?))', data[value]['Line_Data']['Value'], re.IGNORECASE)
                if (Line_Index != None):
                    Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y'], "page_number" : data[value]['Line_Data']['page_number']}                
                    Index_Numbers.append(Case_Details)
            for values in range(len(Index_Numbers)):
                if (values < len(Index_Numbers) -1):
                     Index_1 = Index_Numbers[values]['Index']
                     Index_2 = Index_Numbers[values+1]['Index']
                     batch = []	
                     Batch = []
                     judge_name_all = []
                     for index in range(len(data)):
                         if (index >= Index_1 and index < Index_2) and data[index]['Line_Data']['page_number'] == Index_Numbers[values]['page_number']:
                             batch.append(data[index])
                         else:
                             continue
                     Batch = sorted(batch, key=
                                            lambda x: (round(x['Line_Data']['leftpoint_x'], 0)))
                     Value_Tuple = information_extractor(Batch)                   
                     Case_Numbers.append(excel_generator(Value_Tuple)[0])
                     Party_Names.append(excel_generator(Value_Tuple)[1])
                     Advocate_Names.append(excel_generator(Value_Tuple)[2])
                     Judge_Name_Causelist = metadata_extractor(data)[0]
                     Court_Numbers = metadata_extractor(data)[1]
                     court_number = ""
                     for Hearing in range(len(Hearing_Type)):
                        if (Hearing < len(Hearing_Type) -1):
                            if (Hearing_Type[Hearing+1]['Index'] > Index_Numbers[values]['Index'] > Hearing_Type[Hearing]['Index']):
                                Hearing_Types = []
                                #print (Hearing_Type[Hearing]['Line_Data']['Value'])
                                Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())                                
                            else:
                                Hearing+=1
                        else:
                            if (Index_Numbers[values]['Index'] > Hearing_Type[Hearing]['Index']):
                                Hearing_Types = []
                                #print (Hearing_Type[Hearing]['Line_Data']['Value'])
                                Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())
                     for Judge in range(len(Judge_Name_Causelist)):
                         if (Judge < len(Judge_Name_Causelist) -1):
                             if (Judge_Name_Causelist[Judge+1]['Index'] > Index_Numbers[values]['Index'] > Judge_Name_Causelist[Judge]['Index']):
                                 judge_name_all = []
                                 for name in Judge_Name_Causelist[Judge]['judge_name']:
                                     judge_name = {"name": name.replace("\n", "")}
                                     judge_name_all.append(judge_name)
                             else:
                                Judge+=1
                         else:
                            if (Index_Numbers[values]['Index'] > Judge_Name_Causelist[Judge]['Index']):
                                judge_name_all = []
                                for name in Judge_Name_Causelist[Judge]['judge_name']:
                                    judge_name = {"name": name.replace("\n", "")}
                                    judge_name_all.append(judge_name)
                     for Court in range(len(Court_Numbers)):
                         if (Court < len(Court_Numbers) -1):
                             if (Court_Numbers[Court+1]['Index'] > Index_Numbers[values]['Index'] > Court_Numbers[Court]['Index']):
                                 court_number = Court_Numbers[Court]['court_number'].strip()
                             else:
                                Court+=1
                         else:
                            if (Index_Numbers[values]['Index'] > Court_Numbers[Court]['Index']):
                                court_number = Court_Numbers[Court]['court_number'].strip()
                     json_generator(Value_Tuple, judge_name_all, court_number, Hearing_Types)  
                     Batches.append(Batch)
                     JSON_Complete_Data.append(json_generator(Value_Tuple, judge_name_all, court_number, Hearing_Types))
                # else:
                #      Index_1 = Index_Numbers[values]['Index']
                #      batch = []	
                #      Batch = []
                #      for index in range(len(data)):
                #          if (index >= Index_1) and data[index]['Line_Data']['page_number'] == Index_Numbers[values]['page_number']:
                #              batch.append(data[index])
                #          else:
                #              continue
                #      Batch = sorted(batch, key=
                #                             lambda x: (round(x['Line_Data']['leftpoint_x'], 0)))
                #      Value_Tuple = information_extractor(Batch)
                #      json_generator(Value_Tuple)
                #      Case_Numbers.append(excel_generator(Value_Tuple)[0])
                #      Party_Names.append(excel_generator(Value_Tuple)[1])
                #      Advocate_Names.append(excel_generator(Value_Tuple)[2])
                #      Batches.append(Batch)
                #      JSON_Complete_data.append(json_generator(Value_Tuple))
            Counter = 0
            for value in range(len(JSON_Complete_Data)):
                if (value < len(JSON_Complete_Data)-1):
                    if (JSON_Complete_Data[value]["judge_name"] == JSON_Complete_Data[value+1]["judge_name"]):
                        Counter += 1
                        Serial_Number = "S.No. " + str(Counter)
                        Court_Number = {"court_number" : JSON_Complete_Data[value]["court_number"] + " " + Serial_Number}
                        #JSON_Data["court_number"] = JSON_Data["court_number"] + " " + Serial_Number
                        JSON_Complete_Data[value].update(Court_Number)
                        Serial_Number = ""
                    else:
                        Counter = 0
            # print (JSON_Complete_Data)
            # with open("Output.txt", "w") as f:
            #     f.write(str(JSON_Complete_Data))
            for value in JSON_Complete_Data:
                if (value["party_names"].strip() != ""):
                    user_collection.insert_one(value)
                #container_client.upsert_item(value)

def information_extractor(batch):
    Case_Num = []
    Party = []
    Advocate_Name = []
    for value in range(len(batch)):
        if (batch[value]['Line_Data']['leftpoint_x'] < 100):
            # if ("CRL.A. 324/2016" in batch[value]['Line_Data']['Value']):
            #     print (batch[value]['Line_Data']['Value'])
            value_list = [i for i in batch[value]['Line_Data']['Value'].split("    ") if re.sub(r'(\d\.\s)', "", i.replace("\n","").replace(" |","")).strip()]
            if (len(value_list) == 3) and "registrar" not in batch[value]['Line_Data']['Value'].lower():
                if (Case_Regex.search(value_list[0].strip()) and len(value_list[0].strip()) < 35):
                    Case_Num.append(value_list[0].strip())
                Party.append(value_list[1].strip())
                Advocate_Name.append(value_list[2].strip())
            elif (len(value_list) == 2):
                if (Case_Regex.search(value_list[0].strip()) and len(value_list[0].strip()) < 35):
                    Case_Num.append(value_list[0].strip())
                Party.append(value_list[1].strip())
            elif (len(value_list) == 1):
                if (Case_Regex.search(value_list[0].strip()) and len(value_list[0].strip()) < 35):
                    Case_Num.append(value_list[0].strip())
            else:
                pass
        elif (200 < batch[value]['Line_Data']['leftpoint_x'] < 300):
            value_list = [i for i in batch[value]['Line_Data']['Value'].split("   ") if i.replace("\n","").strip()]
            if (len(value_list) == 2) and "registrar" not in batch[value]['Line_Data']['Value'].lower():
                Party.append(value_list[0].strip())
                Advocate_Name.append(value_list[1].strip())
            elif (len(value_list) == 1):
                Party.append(value_list[0].strip())
            else:
                pass
        elif (batch[value]['Line_Data']['leftpoint_x'] > 350):
            value_list = [i for i in batch[value]['Line_Data']['Value'].split("   ") if i.replace("\n","").strip()]
            if (len(value_list) == 1) and "registrar" not in batch[value]['Line_Data']['Value'].lower():
                Advocate_Name.append(value_list[0].strip())
            else:
                pass
        if(("PETITIONER" in batch[value]['Line_Data']['Value'].upper() or "RESPONDENT" in batch[value]['Line_Data']['Value'].upper()) and batch[value]['Line_Data']['leftpoint_x'] < 100):
            Advocate_Name.append(batch[value]['Line_Data']['Value'].replace("(Petitioner)", "(Petitioner),").replace("(Respondent)", "(Respondent),").strip())
    return (Case_Num, Party, Advocate_Name)
            

def excel_generator(Value_Tuple):
    Cleaned_Case_Number = ", ".join(Value_Tuple[0])
    Cleaned_Party_Names = " ".join(Value_Tuple[1])
    Cleaned_Advocate_Names = " ".join(Value_Tuple[2])
    return(Cleaned_Case_Number, Cleaned_Party_Names, Cleaned_Advocate_Names)


def json_generator(Value_Tuple, judge_name_all, court_number, Hearing_Types):
    advocate_names_all = []
    JSON_Data = {"case_numbers": re.sub(r'\d{1,3}\.\s+', "", excel_generator(Value_Tuple)[0]), "party_names": excel_generator(Value_Tuple)[1]}
    JSON_Data["petitioner_advocate_names"] = []
    JSON_Data["respondent_advocate_names"] = []
    for name in excel_generator(Value_Tuple)[2].split(","):
        advocate_name = {"name": name}
        advocate_names_all.append(advocate_name)
    JSON_Data["advocate_names"] = advocate_names_all
    JSON_Data["additional_details"] = []
    JSON_Data["hearing_details"] = Hearing_Types
    JSON_Data["remarks"] = []
    JSON_Data["judge_name"] = judge_name_all
    JSON_Data["tentative_date"] = ""
    JSON_Data["court_number"] = court_number
    JSON_Data["forum"] = "High Court"
    JSON_Data["date"] = today_date
    JSON_Data["state"] = "Delhi"
    return JSON_Data
    
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