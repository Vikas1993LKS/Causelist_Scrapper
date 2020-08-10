# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 14:54:09 2020

@author: Vikas Gupta
"""


import json
import re
import pandas as pd
import os
import math
import numpy as np
from azure.cosmos import CosmosClient, PartitionKey, exceptions


regexp = re.compile(r'^([0-9])')
listing_details = re.compile(r'(WITH CRIL REV. PETN.)|(Loan settlement matter)|(No Compliance Report)|(Eviction from Land matters)|(Finance & Tax matter)|(Land Records matter)|(Contract matters)|(Compensation matter)|(Supplying GI Pipes (PHED))|(Commerce & Industries)|(E-Tender (PHED))|(Settlement & Land Records)', re.IGNORECASE)
case_regex = re.compile(r'(CRP\(C.R.P.)|(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
case_regex_2nd = re.compile(r'(([0-9]{1,2})(\))(\s+)((CRP\(C.R.P.)|MC\(CRP))|(([0-9]{1,2}(\))(\s+)(With)))|^([0-9](\)|.)).+?(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
date_regex_acceptance = re.compile(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
page_number_rejection = re.compile(r'^([0-9]{1,2})(\/)([0-9]{1,2})$')

def parsepdf(data, download_dir):
    #for file in list1:
        #with open(file, "r") as f:
        #data = json.load(f)
        #file_name = file.split("\\")[-1]
        #print (file_name)
        url = os.environ['ACCOUNT_URI']
        key = os.environ['ACCOUNT_KEY']
        client = CosmosClient(url, credential=key)            
        database_name = "causelist"
        container_name = "causelistcontainer"
        database_client = client.get_database_client(database_name)
        container_client = database_client.get_container_client(container_name)
        Case_Num = []
        Case_Numbers = []
        Party = []
        Petitioner_Advocate = []
        Respondent_Advocate = []
        Hearing_Types = []
        Hearing_Type = []
        Num = []
        Batches = []
        Fault_Files = []
        JSON_Complete_Data = []
        for value in range(len(data)):
            if (regexp.search(data[value-1]['Line_Data']['Value']) and len(data[value]['Line_Data']['Value']) < 60 and case_regex.search(data[value]['Line_Data']['Value']) and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and " in" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                Case_Numbers.append(Case_Details)
            elif (case_regex_2nd.search(data[value]['Line_Data']['Value']) and len(data[value]['Line_Data']['Value']) < 60 and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and "in" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                Case_Numbers.append(Case_Details)
        for values in range(len(Case_Numbers)):
            batch = []
            Batch = []
            Case_Numb = []
            Party_Name = []
            Petitioner_Advocates = []
            Respondent_Advocates = []
            if (values < len(Case_Numbers) -1):
                Index_1 = Case_Numbers[values]['Index']
                Index_2 = Case_Numbers[values+1]['Index']
                Left_point = 0
                for index in range(len(data)):
                    if (data[index]['Line_Data']['font_size'] > 16 and "bold" in data[index]['Line_Data']['font_name'].lower()):
                        #print (data[index]['Line_Data']['Value'])
                        if (data[index] not in Hearing_Type):
                            data[index]['Index'] = index
                            Hearing_Type.append(data[index])
                    if (index >= Index_1 and index < Index_2):
                        if (case_regex.search(data[index]['Line_Data']['Value']) or case_regex_2nd.search(data[index]['Line_Data']['Value'])) and not(date_regex.search(data[index]['Line_Data']['Value'])) and "file" not in data[index]['Line_Data']['Value'] and data[index]['Line_Data']['leftpoint_x'] < 160:
                            Case_Numb.append(re.sub('([0-9]{1,3}\)\s)', "", data[index]['Line_Data']['Value'].strip()).strip())
                        else:
                            pass
                    if (index > Index_1 and index < Index_2) and not(case_regex.search(data[index]['Line_Data']['Value'])) and "VKJNGT+CourierNew,Bold" not in data[index]['Line_Data']['font_name'] and len(data[index]['Line_Data']['Value']) < 70 and not(date_regex.search(data[index]['Line_Data']['Value'])) and not(page_number_rejection.search(data[index]['Line_Data']['Value'].strip().replace("\n",""))) and data[index]['Line_Data']['leftpoint_x'] > Case_Numbers[values]['Left_Point'] and data[index]['Line_Data']['leftpoint_x'] > 100 and "HON'BLE" not in data[index]['Line_Data']['Value'] and "ADJOURNMENT" not in data[index]['Line_Data']['Value'] and "file" not in data[index]['Line_Data']['Value'] and "admission" not in data[index]['Line_Data']['Value'].lower() and "hearing" not in data[index]['Line_Data']['Value'].lower() and "order" not in data[index]['Line_Data']['Value'].lower() and "part" not in data[index]['Line_Data']['Value'].lower() and " pm" not in data[index]['Line_Data']['Value'].lower() and " court" not in data[index]['Line_Data']['Value'].lower() and data[index]['Line_Data']['leftpoint_x'] > 150:
                        batch.append(data[index])
                    else:
                        continue
                Batch = sorted(batch, key=
                                       lambda x: (roundnumber(x['Line_Data']['leftpoint_x'])))
                Count = 0
                for ind in range(len(Batch)):
                    if (ind < len(Batch) -1):
                        if (Count == 0):
                            if (Batch[ind]['Line_Data']['leftpoint_x'] > 100 and Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 5:
                                Party_Name.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x'] 
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['leftpoint_x'] > 100 and Batch[ind]['Line_Data']['Value'] not in Party_Name and Batch[ind]['Line_Data']['leftpoint_x'] == Left_point and Left_point != 0):
                                    Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                else:
                                    Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                        elif (Count == 1):
                            if ((Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 5):
                                Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['Value'] not in Petitioner_Advocates) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 300:
                                        Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                else:
                                    pass
                        elif (Count == 2):
                            if (Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']):
                                Respondent_Advocates.append(Batch[ind]['Line_Data']['Value'].strip())
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x'] 
                            else:
                                Count+=1
                    elif (ind == len(Batch) - 1) and 200 > Batch[ind]['Line_Data']['leftpoint_x'] > 130:
                        Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 290:
                        Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                        Respondent_Advocates.append(Batch[ind]['Line_Data']['Value'].strip().replace("\xa0",""))
                Cleaned_Case_Numbers = ", ".join(Case_Numb)
                JSON_Data = {"case_numbers" : Cleaned_Case_Numbers}
                Cleaned_Petiotioner_Adv = " ".join(Petitioner_Advocates)
                Cleaned_Party = " ".join(Party_Name)
                JSON_Data["party_names"] = Cleaned_Party
                Cleaned_Respondent_Adv = " ".join(Respondent_Advocates)
                JSON_Data["petitioner_advocate_name"] = Cleaned_Petiotioner_Adv.replace("\n", ",")
                JSON_Data["respondent_advocate_name"] = Cleaned_Respondent_Adv.replace("\n", ",")
                JSON_Data["state"] = "Manipur"
                JSON_Complete_Data.append(JSON_Data)
                if len(Case_Numb) != 0:
                    if (len(Party_Name) == 0):
                        Fault_Files.append("For the case_number {}, the Party name is not captured".format(Case_Numb[0]))
                    if " vs" not in Cleaned_Party.lower().replace("\n","") and "V/S" not in Cleaned_Party.replace("\n",""):
                        Fault_Files.append("For the case_number {}, the Party name may be incorrect".format(Case_Numb[0]))
                    if (len(Petitioner_Advocates) == 0):
                        Fault_Files.append("For the case_number {}, the Advocate name is not captured".format(Case_Numb[0]))
                else:
                    pass
                Case_Num.append(Cleaned_Case_Numbers.replace("C.R.P.,","C.R.P.").replace("With, ","With ").replace("CRP,", "CRP "))
                Party.append(Cleaned_Party.replace("\n",""))
                Petitioner_Advocate.append(Cleaned_Petiotioner_Adv.replace("\n",""))
                Respondent_Advocate.append(Cleaned_Respondent_Adv)
                Batches.append(Batch)
            elif (values == len(Case_Numbers) - 1):
                Index_Number = Case_Numbers[values]
                for value in range(len(data)):
                    if value >= Index_Number['Index'] and value <= (Index_Number['Index'] + 12):
                        if data[value]['Line_Data']['leftpoint_x'] < 100 and (case_regex_2nd.search(data[value]['Line_Data']['Value']) or (case_regex.search(data[value]['Line_Data']['Value']))):
                            Case_Numb.append(re.sub('([0-9]{1,3}\))', "",data[value]['Line_Data']['Value']).strip())
                        elif (100 < data[value]['Line_Data']['leftpoint_x'] < 250 and not(date_regex.search(data[value]['Line_Data']['Value']))):
                            Party_Name.append(data[value]['Line_Data']['Value'].strip())
                        elif (250 < data[value]['Line_Data']['leftpoint_x'] < 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
                            Petitioner_Advocates.append(data[value]['Line_Data']['Value'].strip())
                        elif (data[value]['Line_Data']['leftpoint_x'] > 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
                            Respondent_Advocates.append(data[value]['Line_Data']['Value'].strip())
                        else:
                            pass
                Cleaned_Case_Numbers = ", ".join(Case_Numb)
                JSON_Data = {"case_numbers" : Cleaned_Case_Numbers.replace("C.R.P.,","C.R.P.").replace("With, ","With ").replace("CRP,", "CRP ")}
                Cleaned_Petiotioner_Adv = " ".join(Petitioner_Advocates)
                Cleaned_Party = " ".join(Party_Name)
                JSON_Data["party_names"] = Cleaned_Party
                Cleaned_Respondent_Adv = " ".join(Respondent_Advocates)
                JSON_Data["petitioner_advocate_name"] = Cleaned_Petiotioner_Adv.replace("\n", ",")
                JSON_Data["respondent_advocate_name"] = Cleaned_Respondent_Adv.replace("\n", ",")
                JSON_Data["state"] = "Manipur"
                Case_Num.append(Cleaned_Case_Numbers.replace("C.R.P.,","C.R.P.").replace("With, ","With ").replace("CRP,", "CRP "))
                Party.append(Cleaned_Party.replace("\n",""))
                Petitioner_Advocate.append(Cleaned_Petiotioner_Adv.replace("\n",""))
                Respondent_Advocate.append(Cleaned_Respondent_Adv)    
                JSON_Complete_Data.append(JSON_Data)
        for Cases in range(len(Case_Numbers)):
            for Hearing in range(len(Hearing_Type)):
                if (Hearing < len(Hearing_Type) -1):
                    if (Hearing_Type[Hearing+1]['Index'] > Case_Numbers[Cases]['Index'] > Hearing_Type[Hearing]['Index']):
                        Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())                                
                    else:
                        Hearing+=1
                else:
                    if (Case_Numbers[Cases]['Index'] > Hearing_Type[Hearing]['Index']):
                        Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())
        print (JSON_Complete_Data)
        # for value in JSON_Complete_Data:
        #     container_client.upsert_item(value)

# inputlocation=input("Please enter the location of JSON : \n")
# Outputlocation=input("Please enter the location of XML : \n")
# list1=[]

def roundnumber( n ): 
    return int(math.ceil(n / 10.0)) * 10



# def readjson(pathofBundle):
#     for dirpath,dirname,filenames in os.walk(pathofBundle):
#         for file in filenames:
#             try:
#                 if(file.endswith('.json')):
#                     path=(os.path.abspath(os.path.join(dirpath,file)))
#                     list1.append(path)
#                 else:
#                     continue
#             except (FileNotFoundError, IOError):
#                 print("runtime exception")
#     return list1

# readjson(inputlocation)
# parsefiles(list1)