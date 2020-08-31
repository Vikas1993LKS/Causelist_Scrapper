# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 14:54:09 2020

@author: Vikas Gupta
"""


import json
import re
import pandas as pd
import os
# from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pymongo import MongoClient

Case_Regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')


def parsepdf(data, download_dir):
            Case_Numbers = []
            Party_Names = []
            Advocate_Names = []
            Index_Numbers = []
            Batches = []
            JSON_Complete_data = []
            db_name = "causelist"
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
                     for index in range(len(data)):
                         if (index >= Index_1 and index < Index_2) and data[index]['Line_Data']['page_number'] == Index_Numbers[values]['page_number']:
                             batch.append(data[index])
                         else:
                             continue
                     Batch = sorted(batch, key=
                                            lambda x: (round(x['Line_Data']['leftpoint_x'], 0)))
                     Value_Tuple = information_extractor(Batch)
                     json_generator(Value_Tuple)                     
                     Case_Numbers.append(excel_generator(Value_Tuple)[0])
                     Party_Names.append(excel_generator(Value_Tuple)[1])
                     Advocate_Names.append(excel_generator(Value_Tuple)[2])
                     Batches.append(Batch)
                     JSON_Complete_data.append(json_generator(Value_Tuple))
                else:
                     Index_1 = Index_Numbers[values]['Index']
                     batch = []	
                     Batch = []
                     for index in range(len(data)):
                         if (index >= Index_1) and data[index]['Line_Data']['page_number'] == Index_Numbers[values]['page_number']:
                             batch.append(data[index])
                         else:
                             continue
                     Batch = sorted(batch, key=
                                            lambda x: (round(x['Line_Data']['leftpoint_x'], 0)))
                     Value_Tuple = information_extractor(Batch)
                     json_generator(Value_Tuple)
                     Case_Numbers.append(excel_generator(Value_Tuple)[0])
                     Party_Names.append(excel_generator(Value_Tuple)[1])
                     Advocate_Names.append(excel_generator(Value_Tuple)[2])
                     Batches.append(Batch)
                     JSON_Complete_data.append(json_generator(Value_Tuple))
            # print (JSON_Complete_data)
            for value in JSON_Complete_data:
                user_collection.insert_one(value)
                # container_client.upsert_item(value)

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
            Advocate_Name.append(batch[value]['Line_Data']['Value'].strip())
            
    return (Case_Num, Party, Advocate_Name)
            

def excel_generator(Value_Tuple):
    Cleaned_Case_Number = ", ".join(Value_Tuple[0])
    Cleaned_Party_Names = " ".join(Value_Tuple[1])
    Cleaned_Advocate_Names = " ".join(Value_Tuple[2])
    return(Cleaned_Case_Number, Cleaned_Party_Names, Cleaned_Advocate_Names)


def json_generator(Value_Tuple):
    advocate_names_all = []
    JSON_Data = {"case_numbers": re.sub(r'\d{1,3}\.\s+', "", excel_generator(Value_Tuple)[0]), "party_names": excel_generator(Value_Tuple)[1]}
    for name in excel_generator(Value_Tuple)[2].split(","):
        advocate_name = {"name": name}
        advocate_names_all.append(advocate_name)
    JSON_Data["advocate_names"] = advocate_names_all
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