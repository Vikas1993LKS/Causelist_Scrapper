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
#from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pymongo import MongoClient
from Causelist_Metadata.Causelist_Metadata_Extraction import metadata_extractor

regexp = re.compile(r'^([0-9])')
case_regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
case_regex_2nd = re.compile(r'^([0-9](\))).+?(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
date_regex_acceptance = re.compile(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
page_number_rejection = re.compile(r'^([0-9]{1,2})(\/)([0-9]{1,2})$')
today_date = datetime.today().strftime('%d-%m-%Y')
listing_details = re.compile(r'(FOR PRONOUNCEMENT OF JUDGMENT|FOR APPEARANCE|FOR WITHDRAWAL|ADMISSION|INTERLOCUTORY|INTERIM ORDERS|FRESH MATTERS|MOTION HEARING MATTERS|FOR ORDERS|FOR ADMISSION|FINAL DISPOSAL/FINAL HEARING)', re.IGNORECASE)

def parsepdf(data, download_dir):
        Case_Numbers = []
        JSON_Complete_Data = []
        Hearing_Types = []
        Hearing_Type = []
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
        # url = os.environ['ACCOUNT_URI']
        # key = os.environ['ACCOUNT_KEY']
        # client = CosmosClient(url, credential=key)            
        # database_name = "causelist"
        # container_name = "causelistcontainer"
        # database_client = client.get_database_client(database_name)
        # container_client = database_client.get_container_client(container_name)
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
            Case_Numb = []
            Petitioner_Advocate_Name = []
            Respondent_Advocate_Name = []
            Remarks = []
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
                for index in range(len(data)):
                    if (index >= Index_1 and index < Index_2):
                        if (case_regex.search(data[index]['Line_Data']['Value']) or case_regex_2nd.search(data[index]['Line_Data']['Value'])) and not(date_regex.search(data[index]['Line_Data']['Value'])) and "file" not in data[index]['Line_Data']['Value'] and data[index]['Line_Data']['leftpoint_x'] < 160:
                            Case_Numb.append(data[index]['Line_Data']['Value'].strip())
                        else:
                            pass
                    if (index > Index_1 and index < Index_2) and "VKJNGT+CourierNew,Bold" not in data[index]['Line_Data']['font_name'] and len(data[index]['Line_Data']['Value']) < 70 and not(date_regex.search(data[index]['Line_Data']['Value'])) and not(page_number_rejection.search(data[index]['Line_Data']['Value'].replace("\n","").strip())) and data[index]['Line_Data']['leftpoint_x'] > Case_Numbers[values]['Left_Point'] and "HON'BLE" not in data[index]['Line_Data']['Value'] and "file" not in data[index]['Line_Data']['Value'] and "admission" not in data[index]['Line_Data']['Value'].lower() and "hearing" not in data[index]['Line_Data']['Value'].lower() and "order" not in data[index]['Line_Data']['Value'].lower() and "part" not in data[index]['Line_Data']['Value'].lower() and " pm" not in data[index]['Line_Data']['Value'].lower():
                        batch.append(data[index])
                    else:
                        continue
                Batch = sorted(batch, key=
                                       lambda x: (round(x['Line_Data']['leftpoint_x'], 0)))
                # print (Batch)
                Count = 0
                for ind in range(len(Batch)):
                    if (ind < len(Batch) -1):
                        if (Count == 0):
                            if (Batch[ind]['Line_Data']['leftpoint_x'] > 100 and Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 5:
                                Petitioner_Advocate_Name.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x'] 
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['leftpoint_x'] > 100 and Batch[ind]['Line_Data']['Value'] not in Petitioner_Advocate_Name and Batch[ind]['Line_Data']['leftpoint_x'] == Left_point and Left_point != 0):
                                    Petitioner_Advocate_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                else:
                                    Petitioner_Advocate_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                        elif (Count == 1):
                            if ((Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 5):
                                Respondent_Advocate_Name.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['Value'] not in Respondent_Advocate_Name) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 300:
                                        Respondent_Advocate_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                else:
                                    pass
                        elif (Count == 2):
                            if (Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']):
                                Remarks.append(Batch[ind]['Line_Data']['Value'].strip())
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x'] 
                            else:
                                Count+=1
                    elif (ind == len(Batch) - 1) and 200 > Batch[ind]['Line_Data']['leftpoint_x'] > 130:
                        Petitioner_Advocate_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 290:
                        Respondent_Advocate_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                        Remarks.append(Batch[ind]['Line_Data']['Value'].strip().replace("\xa0",""))
                Cleaned_Petitionr_Advocate = ""
                Cleaned_Case_Numbers = ", ".join(Case_Numb)
                for i in range(len(Petitioner_Advocate_Name)):
                    if i < len(Petitioner_Advocate_Name) -1:
                        if (len(Petitioner_Advocate_Name[i+1].split(" ")) == 1) or (len(Petitioner_Advocate_Name[i].split(" ")) == 1):
                            Cleaned_Petitionr_Advocate = Cleaned_Petitionr_Advocate + Petitioner_Advocate_Name[i] + " "
                        else:
                            Cleaned_Petitionr_Advocate = Cleaned_Petitionr_Advocate + Petitioner_Advocate_Name[i] + ", "
                    else:
                        if (len(Petitioner_Advocate_Name[i].split(" ")) == 1):
                            Cleaned_Petitionr_Advocate = Cleaned_Petitionr_Advocate + Petitioner_Advocate_Name[i] + " "
                        else:
                            Cleaned_Petitionr_Advocate = Cleaned_Petitionr_Advocate + Petitioner_Advocate_Name[i] + ", "
                #Cleaned_Petitionr_Advocate = " ".join(Petitioner_Advocate_Name)
                Cleaned_Respondent_Advocate = " ".join(Respondent_Advocate_Name)
                Cleaned_Remarks = " ".join(Remarks)
                JSON_Data = {"case_numbers": Cleaned_Case_Numbers}
                JSON_Data["party_names"] = ""
                JSON_Data["petitioner_advocate_names"] = Cleaned_Petitionr_Advocate.strip().replace("\n","")
                JSON_Data["respondent_advocate_names"] = Cleaned_Respondent_Advocate.strip().replace("\n","").strip()
                JSON_Data["advocate_names"] = []
                JSON_Data["additional_details"] = ""
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
                JSON_Data["district/remarks"] = Cleaned_Remarks.replace("\n",",").strip()
                Judge_Name_Causelist = metadata_extractor(data)[0]
                Court_Numbers = metadata_extractor(data)[1]
                for Judge in range(len(Judge_Name_Causelist)):
                    if (Judge < len(Judge_Name_Causelist) -1):
                        if (Judge_Name_Causelist[Judge+1]['Index'] > Case_Numbers[values]['Index'] > Judge_Name_Causelist[Judge]['Index']):
                            judge_name_all = []
                            for name in Judge_Name_Causelist[Judge]['judge_name']:
                                judge_name = {"name": name.replace("\n", "")}
                                judge_name_all.append(judge_name)
                            JSON_Data["judge_name"] = judge_name_all
                        else:
                            Judge+=1
                    else:
                        if (Case_Numbers[values]['Index'] > Judge_Name_Causelist[Judge]['Index']):
                            judge_name_all = []
                            for name in Judge_Name_Causelist[Judge]['judge_name']:
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
                JSON_Data["state"] = "Andhra Pradesh"
                JSON_Complete_Data.append(JSON_Data)
            # elif (values == len(Case_Numbers) - 1):
            #     Index_Number = Case_Numbers[values]
            #     for value in range(len(data)):
            #         if value >= Index_Number['Index'] and value <= (Index_Number['Index'] + 10):
            #             if data[value]['Line_Data']['leftpoint_x'] < 100 and (case_regex_2nd.search(data[value]['Line_Data']['Value']) or (case_regex.search(data[value]['Line_Data']['Value']))):
            #                 Case_Numb.append(data[value]['Line_Data']['Value'].strip())
            #             elif (100 < data[value]['Line_Data']['leftpoint_x'] < 250 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Petitioner_Advocate_Name.append(data[value]['Line_Data']['Value'].strip())
            #             elif (250 < data[value]['Line_Data']['leftpoint_x'] < 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Respondent_Advocate_Name.append(data[value]['Line_Data']['Value'].strip())
            #             elif (data[value]['Line_Data']['leftpoint_x'] > 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
            #                 Remarks.append(data[value]['Line_Data']['Value'].strip())
            #             else:
            #                 pass
            #     Cleaned_Case_Numbers = ", ".join(Case_Numb)
            #     Cleaned_Petitionr_Advocate = " ".join(Petitioner_Advocate_Name)
            #     Cleaned_Respondent_Advocate = " ".join(Respondent_Advocate_Name)
            #     Cleaned_Remarks = " ".join(Remarks)
            #     JSON_Data = {"case_numbers": Cleaned_Case_Numbers}
            #     JSON_Data["petitioner_advocate_name"] = Cleaned_Petitionr_Advocate.replace("\n",",")
            #     JSON_Data["respondent_advocate_name"] = Cleaned_Respondent_Advocate.replace("\n",",").strip()
            #     JSON_Data["remarks"] = Cleaned_Remarks.replace("\n","").strip()
            #     JSON_Data["state"] = "Andhra Pradesh"
            #     JSON_Complete_Data.append(JSON_Data)
        # with open(Outputlocation + "/" + file_name + "_Batches.txt" ,"w") as f:
        #    for value in Case_Numbers:
        #        f.write(str(value))
        # if (len(Fault_Files) != 0):
        #     with open(Outputlocation + "/" + file_name + "_Error_logs.txt" ,"w") as f:
        #        for value in Fault_Files:
        #            f.write(str(value) + "\n")

        # print (Case_Num)
        # print (Party)
        # print (Jud_Name)
        # print (Advocate_Names_Respondent)
        # df = pd.DataFrame({'Case_Number':Case_Num})
        # df1 = pd.DataFrame({'Petitioner_Advocates':Party})
        # df2 = pd.DataFrame({'Respondent_Advocates': Jud_Name})
        # #df3 = pd.DataFrame({'Listing_Date': Date_List})
        # df3 = pd.DataFrame({'Remarks': Advocate_Names_Respondent})
        # writer = pd.ExcelWriter(Outputlocation + "/" +file_name + ".xlsx")
        # df.to_excel(writer, sheet_name='Sheet1',index=False,startcol=0)
        # df1.to_excel(writer, sheet_name='Sheet1',index=False,startcol=1)                
        # df2.to_excel(writer, sheet_name='Sheet1',index=False,startcol=2)
        # df3.to_excel(writer, sheet_name='Sheet1',index=False,startcol=3)
        # writer.save()
        #print (JSON_Complete_Data)
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
        #print (JSON_Complete_Data)
        for value in JSON_Complete_Data:
            if (value["case_numbers"].strip() != ""):
                user_collection.insert_one(value)
                
