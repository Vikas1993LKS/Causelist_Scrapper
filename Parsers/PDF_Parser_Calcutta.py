# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 15:49:40 2020

@author: vikas
"""

import json
import re
import pandas as pd
import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions


Case_Number_Beginning = re.compile(r'^(\d{1,3}\.)')

Case_Regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')

Whole_data = []

Counters = []

def parsepdf(data, download_dir):
        JSON_Complete_data = []
        Counter = 0
        url = os.environ['ACCOUNT_URI']
        key = os.environ['ACCOUNT_KEY']
        client = CosmosClient(url, credential=key)            
        database_name = "causelist"
        container_name = "causelistcontainer"
        database_client = client.get_database_client(database_name)
        container_client = database_client.get_container_client(container_name)
        for value in data:
                Counter += 1
                Case_data = {"Case_data": value['Line_Data']['Value'], 'index': Counter}
                Whole_data.append(Case_data)
                if (Case_Number_Beginning.search(value['Line_Data']['Value'])):
                    Counters.append(Counter)
        for index in range(len(Counters) - 1):
            batch = []
            advocate_names_all = []
            for value in Whole_data:
                if value['index'] >= Counters[index] and value['index'] < Counters[index + 1] and "page" not in value['Case_data'].lower():
                    batch.append(value)
            if (len(batch) != 0 and len(batch) < 4):
                JSON_Data = {"case_numbers" : batchprocess(batch)[0]}
                JSON_Data["party_names"] = batchprocess(batch)[1]
                for name in batchprocess(batch)[2].split(","):
                    if (name.strip() != ""):
                        advocate_name = {"name": name}
                        advocate_names_all.append(advocate_name)
                    JSON_Data["advocate_names"] = advocate_names_all
                JSON_Complete_data.append(JSON_Data)
        print (JSON_Complete_data)
        # for value in JSON_Complete_data:
        #     container_client.upsert_item(value)

def batchprocess(batch):
    Case_Number = []
    Party = []
    Advocates = []
    Case_Type = ""
    for value in range(len(batch)):
        list1 = [x.strip() for x in batch[value]['Case_data'].split("   ") if x]
        if (len(list1) == 4):
            Serial_Number = list1[0]
            if (Case_Regex.search(list1[1])):
                Case_Number.append(list1[1])
            Party.append(list1[2])
            Advocates.append(list1[3])
        elif (len(list1) == 3):
            if (Case_Regex.search(list1[0])):
                Case_Number.append(list1[0])
            Party.append(list1[1])
            Advocates.append(list1[2])
        elif (len(list1) == 2) and Case_Regex.search(list1[0]):
            if (Case_Regex.search(list1[0])):
                if (len(list1[0].split("  ")) == 2):
                    list1 = list1[0].split("  ")
                    Case_Number.append(list1[0])
                    # Party.append(list1[1])
            Party.append(list1[1])
        elif (len(list1) == 2) and not(Case_Regex.search(list1[0])) and list1[1] == "":
            Party.append(list1[0])
        elif (len(list1) == 1) and not(Case_Regex.search(list1[0])):
            Party.append(list1[0])
    # print (Case_Number)
    # print (Party)
    # print (Advocates)
    Cleaned_Case_Numbers = ", ".join(Case_Number)
    Cleaned_Party_Names = " ".join(Party)
    Cleaned_Advocates = ", ".join(Advocates)
    return (Cleaned_Case_Numbers, Cleaned_Party_Names, Cleaned_Advocates)

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
    