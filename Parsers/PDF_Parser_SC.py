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
import sys
from datetime import datetime
sys.path.append(r'D:\Scrapping\Scrapping\Causelist_Project')
# from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pymongo import MongoClient
from Causelist_Metadata.Causelist_Metadata_Extraction import metadata_extractor

regexp = re.compile(r'^([0-9])')
listing_details = re.compile(r'(WITH CRIL REV. PETN.)|(Loan settlement matter)|(No Compliance Report)|(Eviction from Land matters)|(Finance & Tax matter)|(Land Records matter)|(Contract matters)|(Compensation matter)|(Supplying GI Pipes (PHED))|(Commerce & Industries)|(E-Tender (PHED))|(Settlement & Land Records)', re.IGNORECASE)
case_regex = re.compile(r'(CRP\(C.R.P.|T\.P\.\(C\) No\.|SLP\(Crl\) No\.|SLP\(C\) No.|C.A. No.|T.C.\(C\) No.|Connected)|(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
case_regex_2nd = re.compile(r'(([0-9]{1,3})(\))(\s+)((CRP\(C.R.P.)|MC\(CRP)|CRP\(C.R.P.)|(([0-9]{1,2}(\))(\s+)(With)))|(([0-9]{1,3}(\.)[0-9]{1,2}((\))|(\s+))(With|Connected)))|(([0-9]{1,3}(\.)((\))|(\s+))(With|Connected)))|^([0-9]{1,3}(\)|\.|\s)).+?(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
case_regex_roman_neumeral = re.compile(r'M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}(-[A-Z])?$)')
date_regex_acceptance = re.compile(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
page_number_rejection = re.compile(r'^([0-9]{1,2})(\/)([0-9]{1,2})$|^([0-9]{1,3})$|(Advocate)$|(Petitioner(\s+)?\/(\s+)?Respondent)$')

def parsepdf(data, download_dir):
        today_date = datetime.today().strftime('%d-%m-%Y')
        Case_Num = []
        Case_Numbers = []
        Party = []
        Petitioner_Advocate = []
        Respondent_Advocate = []
        Hearing_Types = []
        Hearing_Type = []
        Num = []
        Batches = []
        Additional_Details = []
        IA_Details = []
        Fault_Files = []
        JSON_Complete_Data = []
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
        # url = os.environ['ACCOUNT_URI']
        # key = os.environ['ACCOUNT_KEY']
        # client = CosmosClient(url, credential=key)            
        # database_name = "causelist"
        # container_name = "causelistcontainer"
        # database_client = client.get_database_client(database_name)
        # container_client = database_client.get_container_client(container_name)
        for value in range(len(data)):
            if (regexp.search(data[value-1]['Line_Data']['Value'].strip()) and "Connected" not in data[value-4]['Line_Data']['Value'] and "Connected" not in data[value-3]['Line_Data']['Value'] and  data[value]['Line_Data']['leftpoint_x'] < 130 and len(data[value]['Line_Data']['Value']) < 60 and case_regex.search(data[value]['Line_Data']['Value']) and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and " in" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                Case_Numbers.append(Case_Details)
            elif (case_regex_2nd.search(data[value]['Line_Data']['Value']) and "Connected" not in data[value-4]['Line_Data']['Value'] and "Connected" not in data[value-3]['Line_Data']['Value'] and data[value]['Line_Data']['leftpoint_x'] < 130 and len(data[value]['Line_Data']['Value']) < 60 and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                Case_Numbers.append(Case_Details)
        for values in range(len(Case_Numbers)):
            batch = []
            Batch = []
            Case_Numb = []
            Party_Name = []
            Petitioner_Advocates = []
            Respondent_Advocates = []
            Additional_Detail = []
            Party_Segreggator = 0
            Page_Numbers = []
            advocate_names_petitioner = []
            advocate_names_respondent = []
            Page_Numbers_List = []
            cleaned_IA_Details = ""
            if (values < len(Case_Numbers) -1):
                Index_1 = Case_Numbers[values]['Index']
                Index_2 = Case_Numbers[values+1]['Index']
                Left_point = 0
                for index in range(len(data)):
                    if (index >= Index_1 and index < Index_2):
                        if (not(date_regex.search(data[index]['Line_Data']['Value']))) and (160 < data[index]['Line_Data']['leftpoint_x'] < 210) and ("HON'BLE" not in data[index]['Line_Data']['Value']) and ("court" not in data[index]['Line_Data']['Value'].lower()) and ("Bold" in data[index]['Line_Data']['font_name']) and (data[index]['Line_Data']['font_size'] < 14):
                            Additional_Detail.append(data[index]['Line_Data']['Value'].strip())
                        else:
                            pass
                    if (data[index]['Line_Data']['font_size'] > 16 and "bold" in data[index]['Line_Data']['font_name'].lower()):
                        if (data[index] not in Hearing_Type):
                            data[index]['Index'] = index
                            Hearing_Type.append(data[index])
                    if (index >= Index_1 and index < Index_2):
                        if (case_regex.search(data[index]['Line_Data']['Value']) or case_regex_roman_neumeral.search(data[index]['Line_Data']['Value']) or case_regex_2nd.search(data[index]['Line_Data']['Value'])) and not(page_number_rejection.search(data[index]['Line_Data']['Value'].strip())) and not(date_regex.search(data[index]['Line_Data']['Value'])) and "bold" not in data[index]['Line_Data']['font_name'].lower() and data[index]['Line_Data']['leftpoint_x'] < 110 and len(data[index]['Line_Data']['Value']) < 60:
                            Case_Numb.append(re.sub('^([0-9]{1,3}(\)|\s))|^([0-9]{1,2}\.[0-9]{1,2})', "", data[index]['Line_Data']['Value'].strip()).strip())
                        else:
                            pass
                    if (index > Index_1 and index < Index_2) and not(case_regex.search(data[index]['Line_Data']['Value'])) and "Bold" not in data[index]['Line_Data']['font_name'] and len(data[index]['Line_Data']['Value']) < 70 and not(date_regex.search(data[index]['Line_Data']['Value'])) and not(page_number_rejection.search(data[index]['Line_Data']['Value'].strip().replace("\n",""))) and data[index]['Line_Data']['leftpoint_x'] > Case_Numbers[values]['Left_Point'] and data[index]['Line_Data']['leftpoint_x'] > 100 and "HON'BLE" not in data[index]['Line_Data']['Value'] and "ADJOURNMENT" not in data[index]['Line_Data']['Value'] and "file" not in data[index]['Line_Data']['Value'] and "admission" not in data[index]['Line_Data']['Value'].lower() and "hearing" not in data[index]['Line_Data']['Value'].lower() and "order" not in data[index]['Line_Data']['Value'].lower() and "part " not in data[index]['Line_Data']['Value'] and " pm" not in data[index]['Line_Data']['Value'].lower() and data[index]['Line_Data']['leftpoint_x'] > 150:
                        batch.append(data[index])
                    else:
                        continue
                Batch = sorted(batch, key=
                                       lambda x: (roundnumber(x['Line_Data']['leftpoint_x'])))
                Count = 0
                for ind in range(len(Batch)):
                    if ("versus" in (Batch[ind]['Line_Data']['Value'].lower()) or Batch[ind]['Line_Data']['Value'].lower().strip() == "vs."):
                        Party_Segreggator_leftpoint = Batch[ind]['Line_Data']['leftpoint_y']
                    Party_Segreggator_Page_Num = Batch[ind]['Line_Data']['page_number']
                    Page_Numbers.append(Batch[ind]['Line_Data']['page_number'])
                    Page_Numbers_Set = set(Page_Numbers)
                    Page_Numbers_List = list(Page_Numbers_Set)
                    if (len(Page_Numbers_List) == 1):
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
                                if Batch[ind]['Line_Data']['leftpoint_y'] < Party_Segreggator_leftpoint:
                                    if ((Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 5):
                                        Respondent_Advocates.append(Batch[ind]['Line_Data']['Value'].strip())
                                        #print ("Respondent " + Batch[ind]['Line_Data']['Value'].strip())
                                        Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                                    else:
                                        Count+=1
                                        if(Batch[ind]['Line_Data']['Value'] not in Petitioner_Advocates) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                                            #print ("Respondent2 " + Batch[ind]['Line_Data']['Value'].strip())
                                            Respondent_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0","").strip())
                                        else:
                                            pass
                                elif Batch[ind]['Line_Data']['leftpoint_y'] > Party_Segreggator_leftpoint:
                                    if ((Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 5):
                                        Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'].strip())
                                        Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                                    else:
                                        Count+=1
                                        if(Batch[ind]['Line_Data']['Value'] not in Petitioner_Advocates) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                                            Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0","").strip())
                                        else:
                                            pass
                        elif (ind == len(Batch) - 1) and 200 > Batch[ind]['Line_Data']['leftpoint_x'] > 130:
                            Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                        elif (ind == len(Batch) - 1) and ((Batch[ind]['Line_Data']['leftpoint_y'] > Party_Segreggator_leftpoint)) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                            Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0","").strip())
                        elif (ind == len(Batch) - 1) and (Batch[ind]['Line_Data']['leftpoint_y'] < Party_Segreggator_leftpoint) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                            Respondent_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0","").strip())
                    else:
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
                                if Party_Segreggator_Page_Num == Page_Numbers_List[1]:
                                    if ((Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 5):
                                        Respondent_Advocates.append(Batch[ind]['Line_Data']['Value'].strip())
                                        #print ("Respondent3 " + Batch[ind]['Line_Data']['Value'].strip())
                                        Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                                    else:
                                        Count+=1
                                        if(Batch[ind]['Line_Data']['Value'] not in Petitioner_Advocates) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                                            #print ("Respondent4 " + Batch[ind]['Line_Data']['Value'].strip())
                                            Respondent_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0","").strip())
                                        else:
                                            pass
                                elif Party_Segreggator_Page_Num == Page_Numbers_List[0]:
                                    if ((Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 5):
                                        Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'].strip())
                                        Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                                    else:
                                        Count+=1
                                        if(Batch[ind]['Line_Data']['Value'] not in Petitioner_Advocates) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                                            Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0","").strip())
                                        else:
                                            pass
                        elif (ind == len(Batch) - 1) and 200 > Batch[ind]['Line_Data']['leftpoint_x'] > 130:
                            Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                        elif (ind == len(Batch) - 1) and (Party_Segreggator_Page_Num == Page_Numbers_List[0]) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                            Petitioner_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0","").strip())
                        elif (ind == len(Batch) - 1) and (Party_Segreggator_Page_Num == Page_Numbers_List[1]) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                            Respondent_Advocates.append(Batch[ind]['Line_Data']['Value'].replace("\xa0","").strip())
                Cleaned_Case_Numbers = ", ".join(Case_Numb)
                JSON_Data = {"case_numbers" : Cleaned_Case_Numbers}
                Cleaned_Party = " ".join(Party_Name)
                JSON_Data["party_names"] = Cleaned_Party.replace("\n","")
                Cleaned_Petitioner_Adv = "".join(Petitioner_Advocates)
                for name in Cleaned_Petitioner_Adv.split(","):
                    advocate_name = {"name": name}
                    advocate_names_petitioner.append(advocate_name)
                JSON_Data["petitioner_advocate_names"] = advocate_names_petitioner
                Cleaned_Respondent_Adv = "".join(Respondent_Advocates)
                for name in Cleaned_Respondent_Adv.split(","):
                    advocate_name = {"name": name}
                    advocate_names_respondent.append(advocate_name)
                JSON_Data["respondent_advocate_names"] = advocate_names_respondent
                JSON_Data["advocate_names"] = []
                Cleaned_Additional_Details = " ".join(Additional_Detail)
                if (additional_details(Cleaned_Additional_Details) != None):
                    cleaned_IA_Details = ", ".join(additional_details(Cleaned_Additional_Details))
                else:
                    cleaned_IA_Details = ""
                JSON_Data["additional_details"] = cleaned_IA_Details
                if len(Case_Numb) != 0:
                    if (len(Party_Name) == 0):
                        Fault_Files.append("For the case_number {}, the Party name is not captured".format(Case_Numb[0]))
                    if " vs" not in Cleaned_Party.lower().replace("\n","") and "V/S" not in Cleaned_Party.replace("\n",""):
                        Fault_Files.append("For the case_number {}, the Party name may be incorrect".format(Case_Numb[0]))
                    if (len(Petitioner_Advocates) == 0):
                        Fault_Files.append("For the case_number {}, the Advocate name is not captured".format(Case_Numb[0]))
                else:
                    pass
                Judge_Name = metadata_extractor(data)[0]
                Court_Numbers = metadata_extractor(data)[1]
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
                if (len(Judge_Name) != 0):
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
                else:
                    JSON_Data["judge_name"] = []
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
                JSON_Data["forum"] = "Supreme Court"
                JSON_Data["date"] =  today_date
                JSON_Data["state"] = "Supreme Court"
                Case_Num.append(Cleaned_Case_Numbers.replace("in,","in").replace("C.R.P.,","C.R.P.").replace("With, ","With ").replace("CRP,", "CRP "))
                Party.append(Cleaned_Party.replace("\n",""))
                Petitioner_Advocate.append(Cleaned_Petitioner_Adv)
                Respondent_Advocate.append(Cleaned_Respondent_Adv)
                Additional_Details.append(Cleaned_Additional_Details)
                IA_Details.append(cleaned_IA_Details)
                JSON_Complete_Data.append(JSON_Data)
                Batches.append(Batch)
            # elif (values == len(Case_Numbers) - 1):
            #     Index_Number = Case_Numbers[values]
            #     for value in range(len(data)):
            #         if value >= Index_Number['Index'] and value <= (Index_Number['Index'] + 12):
            #             if data[value]['Line_Data']['leftpoint_x'] < 100 and (case_regex_2nd.search(data[value]['Line_Data']['Value']) or (case_regex.search(data[value]['Line_Data']['Value']))):
            #                 Case_Numb.append(re.sub('([0-9]{1,3}\))', "",data[value]['Line_Data']['Value']).strip())
            #             elif (100 < data[value]['Line_Data']['leftpoint_x'] < 250 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Party_Name.append(data[value]['Line_Data']['Value'].strip())
            #             elif (data[value]['Line_Data']['leftpoint_y'] < Party_Segreggator_leftpoint and data[value]['Line_Data']['leftpoint_x'] > 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Respondent_Advocates.append(data[value]['Line_Data']['Value'].strip())
            #             elif (data[value]['Line_Data']['leftpoint_y'] > Party_Segreggator_leftpoint and data[value]['Line_Data']['leftpoint_x'] > 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Petitioner_Advocates.append(data[value]['Line_Data']['Value'].strip())
            #             else:
            #                 pass
            #     for Hearing in range(len(Hearing_Type)):
            #         if (Hearing < len(Hearing_Type) -1):
            #             if (Hearing_Type[Hearing+1]['Index'] > Case_Numbers[values]['Index'] > Hearing_Type[Hearing]['Index']):
            #                 Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())                                
            #             else:
            #                 Hearing+=1
            #         else:
            #             if (Case_Numbers[values]['Index'] > Hearing_Type[Hearing]['Index']):
            #                 Hearing_Types.append(Hearing_Type[Hearing]['Line_Data']['Value'].strip())
            #     Cleaned_Case_Numbers = ", ".join(Case_Numb)
            #     Cleaned_Party = " ".join(Party_Name)
            #     Cleaned_Respondent_Adv = "".join(Respondent_Advocates)
            #     Cleaned_Petitioner_Adv = "".join(Petitioner_Advocates)
            #     Cleaned_Additional_Details = " ".join(Additional_Detail)
            #     Case_Num.append(Cleaned_Case_Numbers.replace("in,","in").replace("C.R.P.,","C.R.P.").replace("With, ","With ").replace("CRP,", "CRP "))
            #     Party.append(Cleaned_Party.replace("\n",""))
            #     Petitioner_Advocate.append(Cleaned_Petitioner_Adv)
            #     Respondent_Advocate.append(Cleaned_Respondent_Adv)
            #     Additional_Details.append(Cleaned_Additional_Details)    
        #print (JSON_Complete_Data)
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
        #print (JSON_Complete_Data)
        for value in range(len(JSON_Complete_Data)):
            if ("connected" in JSON_Complete_Data[value]["case_numbers"].lower()):
                index = value
                for i in range(index, -1, -1):
                    if ("connected" not in JSON_Complete_Data[i]["case_numbers"].lower()):
                        associated_case_number = JSON_Complete_Data[i]["case_numbers"]
                        remarks = {"remarks": "in association with " + associated_case_number}
                        JSON_Complete_Data[value].update(remarks)
                        break
        # with open("Output.txt", "w") as f:
        #     f.write(str(JSON_Complete_Data))
        for value in JSON_Complete_Data:
            user_collection.insert_one(value)
            #container_client.upsert_item(value)

def additional_details(Additional_Detail):
    links = []
    IA_Links = re.findall(r'(ia\s+No\.(\s+)?[0-9]+\/[0-9]+(\s)?(-)\s?([A-Z-\.\s(\/)?]+))', Additional_Detail.replace("IA","ia"))
    for value in IA_Links:
        for link in  range(len(value)):
            if (link == 0):
                if value[link].strip() != "":
                    links.append(value[link].replace("ia ", "IA "))
    return (links)

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