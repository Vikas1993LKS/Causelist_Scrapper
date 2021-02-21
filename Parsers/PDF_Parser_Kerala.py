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
import sys
from datetime import datetime
#from azure.cosmos import CosmosClient, PartitionKey, exceptions
sys.path.append(r'D:\Scrapping\Scrapping\Causelist_Project')
# from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pymongo import MongoClient
from Causelist_Metadata.Causelist_Metadata_Extraction import metadata_extractor


regexp = re.compile(r'^([0-9])')
case_regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
case_regex_2nd = re.compile(r'^([0-9](\)|.)).+?(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
date_regex_acceptance = re.compile(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
page_number_rejection = re.compile(r'^([0-9]{1,2})(\/)([0-9]{1,2})$')
today_date = datetime.today().strftime('%d-%m-%Y')
listing_details = re.compile(r'(PART HEARD|DEFECT|CONTEMPT OF COURT|FOR APPEARANCE|FOR HEARING|PETITIONS|FOR JUDGEMENT|ADMISSION|INTERLOCUTORY|INTERIM ORDERS|FRESH MATTERS|MOTION HEARING MATTERS|FOR ORDERS|FOR ADMISSION|CONDONATION OF FILING DELAY|FINAL DISPOSAL/FINAL HEARING|FOR DISPOSAL)', re.IGNORECASE)
connected_case = re.compile(r'([0-9]{1,3}\.[0-9]{1,2})')

def parsepdf(data, download_dir):
        Hearing_Types = []
        Hearing_Type = []        
        Case_Num = []
        Case_Numbers = []
        Party = []
        Jud_Name = []
        Date_List = []
        Advocate_Names_Respondent = []
        Num = []
        Batches = []
        Fault_Files = []
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
            if ("bold" in data[index]['Line_Data']['font_name'].lower()) and (listing_details.search(data[index]['Line_Data']['Value'].strip())):
                if (data[index] not in Hearing_Type):
                    data[index]['Index'] = index
                    Hearing_Type.append(data[index])
        for value in range(len(data)):
            if (regexp.search(data[value-1]['Line_Data']['Value']) and len(data[value]['Line_Data']['Value']) < 60 and case_regex.search(data[value]['Line_Data']['Value']) and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and " in" not in data[value]['Line_Data']['Value'].lower() and "with" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                Case_Numbers.append(Case_Details)
            elif (case_regex_2nd.search(data[value]['Line_Data']['Value']) and len(data[value]['Line_Data']['Value']) < 60 and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and "in" not in data[value]['Line_Data']['Value'].lower() and "with" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                Case_Numbers.append(Case_Details)
        for values in range(len(Case_Numbers)):
            batch = []
            Batch = []
            Adv_Name = []
            Case_Numb = []
            Party_Name = []
            Judge_Name = []
            if (values < len(Case_Numbers) -1):
                Index_1 = Case_Numbers[values]['Index']
                Index_2 = Case_Numbers[values+1]['Index']
                Left_point = 0
                for index in range(len(data)):
                    if (index >= Index_1 and index < Index_2):
                        if (connected_case.search(data[index-1]['Line_Data']['Value']) and case_regex.search(data[index]['Line_Data']['Value']) or case_regex_2nd.search(data[index]['Line_Data']['Value'])) and not(date_regex.search(data[index]['Line_Data']['Value'])) and "file" not in data[index]['Line_Data']['Value'] and data[index]['Line_Data']['leftpoint_x'] < 160:
                            Case_Numb.append(data[index]['Line_Data']['Value'].strip().replace("\n", "") + " connected case")
                        elif (case_regex.search(data[index]['Line_Data']['Value']) or case_regex_2nd.search(data[index]['Line_Data']['Value'])) and not(date_regex.search(data[index]['Line_Data']['Value'])) and "file" not in data[index]['Line_Data']['Value'] and data[index]['Line_Data']['leftpoint_x'] < 160:
                            Case_Numb.append(data[index]['Line_Data']['Value'].strip().replace("\n", ""))
                        else:
                            pass
                    if (index > Index_1 and index < Index_2) and not(case_regex.search(data[index]['Line_Data']['Value'])) and "VKJNGT+CourierNew,Bold" not in data[index]['Line_Data']['font_name'] and len(data[index]['Line_Data']['Value']) < 70 and not(date_regex.search(data[index]['Line_Data']['Value'])) and not(page_number_rejection.search(data[index]['Line_Data']['Value'].strip().replace("\n",""))) and data[index]['Line_Data']['leftpoint_x'] > Case_Numbers[values]['Left_Point'] and data[index]['Line_Data']['leftpoint_x'] > 100 and "HON'BLE" not in data[index]['Line_Data']['Value'] and "file" not in data[index]['Line_Data']['Value'] and "admission" not in data[index]['Line_Data']['Value'].lower() and "hearing" not in data[index]['Line_Data']['Value'].lower() and "order" not in data[index]['Line_Data']['Value'].lower() and " part" not in data[index]['Line_Data']['Value'].lower() and " pm" not in data[index]['Line_Data']['Value'].lower() and " court" not in data[index]['Line_Data']['Value'].lower() and data[index]['Line_Data']['leftpoint_x'] > 150:
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
                                Adv_Name.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['Value'] not in Judge_Name) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 300:
                                        Adv_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                else:
                                    pass
                        # elif (Count == 2):
                        #     if (Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']):
                        #         Adv_Name.append(Batch[ind]['Line_Data']['Value'].strip())
                        #         Left_point = Batch[ind]['Line_Data']['leftpoint_x'] 
                        #     else:
                        #         Count+=1
                    elif (ind == len(Batch) - 1) and 200 > Batch[ind]['Line_Data']['leftpoint_x'] > 130:
                        Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 290:
                        Judge_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                        Adv_Name.append(Batch[ind]['Line_Data']['Value'].strip().replace("\xa0",""))
                Cleaned_Case_Numbers = ", ".join(Case_Numb)
                #Cleaned_Judge = " ".join(Judge_Name)
                Cleaned_Party = " ".join(Party_Name)
                Cleaned_Adv_Name = " ".join(Adv_Name)
                Cleaned_Adv_Name = Cleaned_Adv_Name.replace("\n", ", ")
                Petitioner_Advocate_Name_all = []
                Respondent_Advocate_Name_all = []
                Advocate_Name_all = []
                if len(Case_Numb) != 0:
                    if (len(Party_Name) == 0):
                        Fault_Files.append("For the case_number {}, the Party name is not captured".format(Case_Numb[0]))
                    if " vs" not in Cleaned_Party.lower().replace("\n","") and "V/S" not in Cleaned_Party.replace("\n",""):
                        #print (Cleaned_Party.replace("\n",""))
                        Fault_Files.append("For the case_number {}, the Party name may be incorrect".format(Case_Numb[0]))
                    if (len(Judge_Name) == 0):
                        Fault_Files.append("For the case_number {}, the Advocate name is not captured".format(Case_Numb[0]))
                else:
                    pass
                Party.append(Cleaned_Party.replace("\n",""))
                #Jud_Name.append(Cleaned_Judge.replace("\n",""))
                Case_Num.append(Cleaned_Case_Numbers)
                Advocate_Names_Respondent.append(Cleaned_Adv_Name)
                Batches.append(Batch)
                JSON_Data = {"case_numbers": Cleaned_Case_Numbers.strip()}
                JSON_Data["party_names"] = Cleaned_Party.replace("\n", "")
                if ("/") in Cleaned_Adv_Name:
                    for name in Cleaned_Adv_Name.replace("\n",",").split("/")[0].strip().split(","):
                        if (name.strip() != ""):
                            advocate_name = {"name": name.strip()}
                            Petitioner_Advocate_Name_all.append(advocate_name)
                    JSON_Data["petitioner_advocate_names"] = Petitioner_Advocate_Name_all
                    for name in Cleaned_Adv_Name.replace("\n",",").split("/")[1].strip().split(","):
                        if (name.strip() != ""):
                            advocate_name = {"name": name.strip()}
                            Respondent_Advocate_Name_all.append(advocate_name)
                    JSON_Data["respondent_advocate_names"] = Respondent_Advocate_Name_all
                    JSON_Data["advocate_names"] = []
                else:
                    JSON_Data["petitioner_advocate_names"] = []
                    JSON_Data["respondent_advocate_names"] = []
                    for name in Cleaned_Adv_Name.replace("\n",",").strip().split(","):
                        if (name.strip() != ""):
                            advocate_name = {"name": name.strip()}
                            Advocate_Name_all.append(advocate_name)
                    JSON_Data["advocate_names"] = Advocate_Name_all
                JSON_Data["additional_details"] = []
                for Hearing in range(len(Hearing_Type)):
                    if (Hearing < len(Hearing_Type) -1):
                        if (Hearing_Type[Hearing+1]['Index'] > Case_Numbers[values]['Index'] > Hearing_Type[Hearing]['Index']):
                            #print (Hearing_Type[Hearing]['Line_Data']['Value'])
                            Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())                                
                            JSON_Data["hearing_details"] = Hearing_Type[Hearing]['Line_Data']['Value'].strip()
                        else:
                            Hearing+=1
                    else:
                        if (Case_Numbers[values]['Index'] > Hearing_Type[Hearing]['Index']):
                            #print (Hearing_Type[Hearing]['Line_Data']['Value'])
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
                        if (Case_Numbers[values]['Index'] > Court_Numbers[Court]['Index']):
                            JSON_Data["court_number"] = Court_Numbers[Court]['court_number'].strip()
                JSON_Data["forum"] = "High Court"
                JSON_Data["date"] = today_date
                JSON_Data["state"] = "Kerala"
                JSON_Complete_Data.append(JSON_Data)
            # elif (values == len(Case_Numbers) - 1):
            #     Index_Number = Case_Numbers[values]
            #     for value in range(len(data)):
            #         if value >= Index_Number['Index'] and value <= (Index_Number['Index'] + 10):
            #             if data[value]['Line_Data']['leftpoint_x'] < 100 and (case_regex_2nd.search(data[value]['Line_Data']['Value']) or (case_regex.search(data[value]['Line_Data']['Value']))):
            #                 Case_Numb.append(data[value]['Line_Data']['Value'].strip())
            #             elif (100 < data[value]['Line_Data']['leftpoint_x'] < 250 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Party_Name.append(data[value]['Line_Data']['Value'].strip())
            #             elif (250 < data[value]['Line_Data']['leftpoint_x'] < 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Adv_Name.append(data[value]['Line_Data']['Value'].strip())
            #             # elif (data[value]['Line_Data']['leftpoint_x'] > 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #             #     Adv_Name.append(data[value]['Line_Data']['Value'].strip())
            #             else:
            #                 pass
            #     Cleaned_Case_Numbers = ", ".join(Case_Numb)
            #     #Cleaned_Judge = " ".join(Judge_Name)
            #     Cleaned_Party = " ".join(Party_Name)
            #     Cleaned_Adv_Name = " ".join(Adv_Name)
            #     Cleaned_Adv_Name = Cleaned_Adv_Name.replace("\n", ", ")
            #     #Cleaned_Date_List = ", ".join(Datelist)
            #     Party.append(Cleaned_Party.replace("\n",""))
            #     #Jud_Name.append(Cleaned_Judge.replace("\n",""))
            #     #Date_List.append(Cleaned_Date_List.replace("\n",""))
            #     Case_Num.append(Cleaned_Case_Numbers)
            #     Advocate_Names_Respondent.append(Cleaned_Adv_Name)
            #     JSON_Data = {"case_numbers": Cleaned_Case_Numbers}
            #     JSON_Data["party_name"] = Cleaned_Party.replace("\n", "")
            #     if ("/") in Cleaned_Adv_Name:
            #         JSON_Data["petitioner_advocate_name"] = Cleaned_Adv_Name.replace("\n",",").split("/")[0].strip()
            #         JSON_Data["respondent_advocate_name"] = Cleaned_Adv_Name.replace("\n",",").split("/")[1].strip()
            #     else:
            #         JSON_Data["petitioner_advocate_name"] = Cleaned_Adv_Name.replace("\n",",").strip()                
            #     JSON_Data["state"] = "Kerala"
            #     JSON_Complete_Data.append(JSON_Data)
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
                    Counter += 1
                    Serial_Number = "S.No. " + str(Counter)
                    Court_Number = {"court_number" : JSON_Complete_Data[value]["court_number"] + " " + Serial_Number}
                    #JSON_Data["court_number"] = JSON_Data["court_number"] + " " + Serial_Number
                    JSON_Complete_Data[value].update(Court_Number)
                    Serial_Number = ""
                    Counter = 0
        for value in range(len(JSON_Complete_Data)):
            if (connected_case.search(JSON_Complete_Data[value]["case_numbers"]) or "connected case" in JSON_Complete_Data[value]["case_numbers"]):
                index = value
                for i in range(index, -1, -1):
                    if (not(connected_case.search(JSON_Complete_Data[i]["case_numbers"].lower())) and "connected case" not in JSON_Complete_Data[i]["case_numbers"]):
                        associated_case_number = JSON_Complete_Data[i]["case_numbers"]
                        remarks = {"remarks": "in association with " + associated_case_number}
                        JSON_Complete_Data[value].update(remarks)
                        break
                case_numbers = {"case_numbers" : re.sub(r"([0-9]{1,3}\.[0-9]{1,2})", "", JSON_Complete_Data[value]["case_numbers"].replace("connected case", ""))}
                JSON_Complete_Data[value].update(case_numbers)
        # print (JSON_Complete_Data)
        # with open("Input.txt", "w") as f:
        #     f.write(str(data))
        # with open("Output.txt", "w") as f:
        #     f.write(str(JSON_Complete_Data))
        for value in JSON_Complete_Data:
            if (value["party_names"].strip() != ""):
                user_collection.insert_one(value)

def roundnumber( n ): 
    return int(math.ceil(n / 10.0)) * 10