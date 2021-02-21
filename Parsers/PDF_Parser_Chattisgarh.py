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
from datetime import datetime
#from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pymongo import MongoClient
from Causelist_Metadata.Causelist_Metadata_Extraction import metadata_extractor


regexp = re.compile(r'^(^([0-9]{1,2}.|[0-9]{1,2}))')
listing_details = re.compile(r'(MOTION HEARING MATTERS|FINAL DISPOSAL/FINAL HEARING|FOR HEARING AND DISPOSAL|FOR ORDERS|FRESH MATTERS|WITH CRIL REV. PETN.)|(Loan settlement matter)|(No Compliance Report)|(Eviction from Land matters)|(Finance & Tax matter)|(Land Records matter)|(Contract matters)|(Compensation matter)|(Supplying GI Pipes (PHED))|(Commerce & Industries)|(E-Tender (PHED))|(Settlement & Land Records)', re.IGNORECASE)
case_regex = re.compile(r'(CRP\(C.R.P.)|(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
case_regex_2nd = re.compile(r'(([0-9]{1,2})(\)|\.)(\s+)((CRP\(C.R.P.)|MC\(CRP))|(([0-9]{1,2}(\))(\s+)(With)))|^([0-9](\)|.)).+?(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
date_regex_acceptance = re.compile(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
page_number_rejection = re.compile(r'^([0-9]{1,2})(\/)([0-9]{1,2})$')
today_date = datetime.today().strftime('%d-%m-%Y')

def parsepdf(data, download_dir):
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
        last_index = 0
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
        for value in range(len(data)):
            if ("list of defective cases" in data[value]['Line_Data']['Value'].lower()):
                last_index = value
                break
        if (last_index > 0):
            for value in range(last_index):
                if (regexp.search(data[value-1]['Line_Data']['Value']) and len(data[value]['Line_Data']['Value']) < 60 and case_regex.search(data[value]['Line_Data']['Value']) and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and " in" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                    Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                    Case_Numbers.append(Case_Details)
                elif (case_regex_2nd.search(data[value]['Line_Data']['Value']) and len(data[value]['Line_Data']['Value']) < 60 and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and "in" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                    Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                    Case_Numbers.append(Case_Details)
        else:
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
            Remarks = ""
            if (values < len(Case_Numbers) -1):
                Index_1 = Case_Numbers[values]['Index']
                Index_2 = Case_Numbers[values+1]['Index']
                Left_point = 0
                for index in range(len(data)):
                    if ("bold" in data[index]['Line_Data']['font_name'].lower() and listing_details.search(data[index]['Line_Data']['Value'])):
                        #print (data[index]['Line_Data']['Value'])
                        if (data[index] not in Hearing_Type):
                            data[index]['Index'] = index
                            Hearing_Type.append(data[index])
                    if (index >= Index_1 and index < Index_2):
                        if (case_regex.search(data[index]['Line_Data']['Value']) or case_regex_2nd.search(data[index]['Line_Data']['Value'])) and not(date_regex.search(data[index]['Line_Data']['Value'])) and "file" not in data[index]['Line_Data']['Value'] and data[index]['Line_Data']['leftpoint_x'] < 160:
                            Case_Numb.append(re.sub('([0-9]{1,3}\)\s)', "", data[index]['Line_Data']['Value'].strip()).strip())
                        else:
                            pass
                    if (index > Index_1 and index < Index_2) and "VKJNGT+CourierNew,Bold" not in data[index]['Line_Data']['font_name'] and not(page_number_rejection.search(data[index]['Line_Data']['Value'].strip().replace("\n",""))) and not(date_regex.search(data[index]['Line_Data']['Value'].strip().replace("\n",""))) and data[index]['Line_Data']['leftpoint_x'] > Case_Numbers[values]['Left_Point'] and data[index]['Line_Data']['leftpoint_x'] > 100 and "HON'BLE" not in data[index]['Line_Data']['Value'] and "court hall" not in data[index]['Line_Data']['Value'].lower() and "justice" not in data[index]['Line_Data']['Value'].lower() and "ADJOURNMENT" not in data[index]['Line_Data']['Value'] and "file" not in data[index]['Line_Data']['Value'] and data[index]['Line_Data']['leftpoint_x'] > 150:
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
                Cleaned_Party = " ".join(Party_Name)
                Cleaned_Petiotioner_Adv = ""
                petitioner_advocate_names_all = []
                Cleaned_Respondent_Adv = ""
                respondent_advocate_names_all = []
                for name in Petitioner_Advocates:
                    if len(name.split(",")) > 1 and len(name.split(",")[-1].split(" ")) < 2:
                        Cleaned_Petiotioner_Adv = Cleaned_Petiotioner_Adv + name + " "
                    else:
                        Cleaned_Petiotioner_Adv = Cleaned_Petiotioner_Adv + name + ", "
                for name in Respondent_Advocates:
                    if len(name.split(",")) > 1 and len(name.split(",")[-1].split(" ")) < 2:
                        Cleaned_Respondent_Adv = Cleaned_Respondent_Adv + name + " "
                    else:
                        Cleaned_Respondent_Adv = Cleaned_Respondent_Adv + name + ", "
                for name in Cleaned_Petiotioner_Adv.split(","):
                    if (name.strip() != ""):
                        advocate_name = {"name": name.replace("\n","")}
                        petitioner_advocate_names_all.append(advocate_name)
                        advocate_name = {}
                for name in Cleaned_Respondent_Adv.split(","):
                    if (name.strip() != ""):
                        advocate_name = {"name": name.replace("\n","")}
                        respondent_advocate_names_all.append(advocate_name)
                        advocate_name = {}
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
                Respondent_Advocate.append(Cleaned_Respondent_Adv.replace("\n",""))
                Batches.append(Batch)
                JSON_Data = {"case_numbers" : re.sub(regexp, "", Cleaned_Case_Numbers.replace("C.R.P.,","C.R.P.").replace("With, ","With ").replace("CRP,", "CRP ").strip())}
                if ("*" in Cleaned_Party):
                    JSON_Data["party_names"] = Cleaned_Party.split("*")[0].strip().replace("\n","")
                    Remarks = Cleaned_Party.split("*")[1].strip().replace("\n","")
                else:
                    JSON_Data["party_names"] = Cleaned_Party.replace("\n","")
                JSON_Data["petitioner_advocate_names"] = petitioner_advocate_names_all
                JSON_Data["respondent_advocate_names"] = respondent_advocate_names_all
                JSON_Data["advocate_names"] = []
                JSON_Data["addtitional_details"] = ""
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
                JSON_Data["remarks"] = Remarks
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
                        else:
                            JSON_Data["court_number"] = ""
                JSON_Data["forum"] = "High Court"
                JSON_Data["date"] = today_date
                JSON_Data["state"] = "Chattisgarh"
                if (JSON_Data["party_names"].strip() != ""):
                    JSON_Complete_Data.append(JSON_Data)
            # elif (values == len(Case_Numbers) - 1):
            #     Index_Number = Case_Numbers[values]
            #     for value in range(len(data)):
            #         if value >= Index_Number['Index'] and value <= (Index_Number['Index'] + 12):
            #             if data[value]['Line_Data']['leftpoint_x'] < 100 and (case_regex_2nd.search(data[value]['Line_Data']['Value']) or (case_regex.search(data[value]['Line_Data']['Value']))):
            #                 Case_Numb.append(re.sub('([0-9]{1,3}\))', "",data[value]['Line_Data']['Value']).strip())
            #             elif (100 < data[value]['Line_Data']['leftpoint_x'] < 250 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Party_Name.append(data[value]['Line_Data']['Value'].strip())
            #             elif (250 < data[value]['Line_Data']['leftpoint_x'] < 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Petitioner_Advocates.append(data[value]['Line_Data']['Value'].strip())
            #             elif (data[value]['Line_Data']['leftpoint_x'] > 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Respondent_Advocates.append(data[value]['Line_Data']['Value'].strip())
            #             else:
            #                 pass
            #     Cleaned_Case_Numbers = ", ".join(Case_Numb)
            #     Cleaned_Petiotioner_Adv = ""
            #     petitioner_advocate_names_all = []
            #     Cleaned_Respondent_Adv = ""
            #     respondent_advocate_names_all = []
            #     for name in Petitioner_Advocate:    
            #         if len(name.split(",")) > 1 and len(name.split(",")[-1].split(" ")) < 2:
            #             Cleaned_Petiotioner_Adv = Cleaned_Petiotioner_Adv + name + " "
            #         else:
            #             Cleaned_Petiotioner_Adv = Cleaned_Petiotioner_Adv + name + ", "
            #     for name in Respondent_Advocates:
            #         if len(name.split(",")) > 1 and len(name.split(",")[-1].split(" ")) < 2:
            #             Cleaned_Respondent_Adv = Cleaned_Petiotioner_Adv + name + " "
            #         else:
            #             Cleaned_Respondent_Adv = Cleaned_Petiotioner_Adv + name + ", "
            #     for name in Cleaned_Petiotioner_Adv.split(","):
            #         if (name.strip() != ""):
            #             advocate_name = {"name": name.replace("\n","")}
            #             petitioner_advocate_names_all.append(advocate_name)
            #     for name in Cleaned_Respondent_Adv.split(","):
            #         if (name.strip() != ""):
            #             advocate_name = {"name": name.replace("\n","")}
            #             respondent_advocate_names_all.append(advocate_name)
            #     Cleaned_Party = " ".join(Party_Name)
            #     JSON_Data = {"case_numbers" : Cleaned_Case_Numbers.replace("C.R.P.,","C.R.P.").replace("With, ","With ").replace("CRP,", "CRP ")}
            #     JSON_Data["party_name"] = Cleaned_Party.replace("\n","")
            #     JSON_Data["petitioner_advocate_name"] = Cleaned_Petiotioner_Adv.replace("\n",",")
            #     JSON_Data["respondent_advocate_name"] = Cleaned_Respondent_Adv.replace("\n",",")
            #     JSON_Data["forum"] = "High Court"
            #     JSON_Data["date"] = today_date
            #     JSON_Data["state"] = "Chattisgarh"
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
        # print (JSON_Complete_Data)
        # with open("Output.txt", "w") as f:
        #     f.write(str(JSON_Complete_Data))
        for value in JSON_Complete_Data:
            if (value["party_names"].strip() != ""):
                user_collection.insert_one(value)

def roundnumber( n ): 
    return int(math.ceil(n / 10.0)) * 10