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
from Causelist_Metadata.Causelist_Metadata_Extraction import metadata_extractor
from pymongo import MongoClient


regexp = re.compile(r'^([0-9])')
case_regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
case_regex_2nd = re.compile(r'^([0-9]).+?(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
date_regex_acceptance = re.compile(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
            
today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)

def parsepdf(data, download_dir):
        Case_Num = []
        Case_Numbers = []
        Party = []
        Jud_Name = []
        Date_List = []
        #Advocate_Names_Respondent = []
        Batches = []
        Fault_Files = []
        JSON_Complete_Data = []
        db_name = os.getenv("MONGO_DB")
        host = os.getenv("MONGO_HOST")
        port = 10255
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")
        args = "ssl=true&retrywrites=false&ssl_cert_reqs=CERT_NONE"
        connection_uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}?{args}"
        client = MongoClient(connection_uri)
        db = client[db_name]
        user_collection = db['user']
        for value in range(len(data)):
            if (regexp.search(data[value-1]['Line_Data']['Value']) and len(data[value]['Line_Data']['Value']) < 60 and case_regex.search(data[value]['Line_Data']['Value']) and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and "in" not in data[value]['Line_Data']['Value'].lower() and "with" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
                Case_Details = {"Value" : data[value]['Line_Data']['Value'], "Index": value, "Left_Point" : data[value]['Line_Data']['leftpoint_x'], "Left_Point_Y" : data[value]['Line_Data']['leftpoint_y']}
                Case_Numbers.append(Case_Details)
            elif (case_regex_2nd.search(data[value]['Line_Data']['Value']) and len(data[value]['Line_Data']['Value']) < 60 and not(date_regex.search(data[value]['Line_Data']['Value'])) and "on appeal" not in data[value]['Line_Data']['Value'].lower() and "on an intended appeal" not in data[value]['Line_Data']['Value'].lower() and "file" not in data[value]['Line_Data']['Value'].lower() and "listed" not in data[value]['Line_Data']['Value'].lower() and "in" not in data[value]['Line_Data']['Value'].lower() and "with" not in data[value]['Line_Data']['Value'].lower() and "&" not in data[value]['Line_Data']['Value'].lower() and " pm" not in data[value]['Line_Data']['Value'].lower() and " am" not in data[value]['Line_Data']['Value'].lower()):
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
                # Datelist = []
                Left_point = 0
                for index in range(len(data)):
                    if (index >= Index_1 and index < Index_2):
                        if (case_regex.search(data[index]['Line_Data']['Value']) or case_regex_2nd.search(data[index]['Line_Data']['Value'])) and not(date_regex.search(data[index]['Line_Data']['Value'])) and "file" not in data[index]['Line_Data']['Value'] and data[index]['Line_Data']['leftpoint_x'] < 160:
                            Case_Numb.append(re.sub(r'^([0-9]{1,2}\s+)', "", data[index]['Line_Data']['Value'].strip()))
                        else:
                            pass
                        # if (date_regex_acceptance.search(data[index]['Line_Data']['Value'])):
                        #     for date in date_regex_acceptance.finditer(data[index]['Line_Data']['Value']):
                        #         Datelist.append(date.group())
                        # else:
                        #     pass
                    if (index > Index_1 and index < Index_2) and "VKJNGT+CourierNew,Bold" not in data[index]['Line_Data']['font_name'] and len(data[index]['Line_Data']['Value']) < 70 and not(date_regex.search(data[index]['Line_Data']['Value'])) and data[index]['Line_Data']['leftpoint_x'] > Case_Numbers[values]['Left_Point'] and data[index]['Line_Data']['leftpoint_x'] > 100 and "HON'BLE" not in data[index]['Line_Data']['Value'] and "file" not in data[index]['Line_Data']['Value'] and "admission" not in data[index]['Line_Data']['Value'].lower() and "hearing" not in data[index]['Line_Data']['Value'].lower() and "order" not in data[index]['Line_Data']['Value'].lower() and "part" not in data[index]['Line_Data']['Value'].lower() and " pm" not in data[index]['Line_Data']['Value'].lower():
                        batch.append(data[index])
                    else:
                        continue
                Batch = sorted(batch, key=
                                       lambda x: (round(x['Line_Data']['leftpoint_x'], 0)))
                Count = 0
                Party_Name = []
                Judge_Name = []
                advocate_names_all = []
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
                            if ((Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']) or (Batch[ind+1]['Line_Data']['leftpoint_x'] - Batch[ind]['Line_Data']['leftpoint_x']) < 10):
                                Judge_Name.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['Value'] not in Judge_Name) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 300:
                                        Judge_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                else:
                                    pass
                    elif (ind == len(Batch) - 1) and 200 > Batch[ind]['Line_Data']['leftpoint_x'] > 130:
                        Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and Batch[ind]['Line_Data']['leftpoint_x'] > 290:
                        Judge_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                if len(Case_Numb) != 0:
                    if (len(Party_Name) == 0):
                        Fault_Files.append("For the case_number {}, the Party name is not captured".format(Case_Numb[0]))
                    if (len(Judge_Name) == 0):
                        Fault_Files.append("For the case_number {}, the Advocate name is not captured".format(Case_Numb[0]))
                else:
                    pass
                Cleaned_Case_Numbers = ", ".join(Case_Numb)
                Cleaned_Judge = " ".join(Judge_Name)
                Cleaned_Judge = Cleaned_Judge.replace("\n", "")
                Cleaned_Party = " ".join(Party_Name)
                # Cleaned_Date_List = ", ".join(Datelist)
                Party.append(Cleaned_Party.replace("\n",""))
                Jud_Name.append(Cleaned_Judge.replace("\n",""))
                # Date_List.append(Cleaned_Date_List.replace("\n",""))
                Case_Num.append(Cleaned_Case_Numbers)
                JSON_Data = {"case_numbers": Cleaned_Case_Numbers}
                JSON_Data["party_names"] = Cleaned_Party.replace("\n", "")
                JSON_Data["petitioner_advocate_names"] = []
                JSON_Data["respondent_advocate_names"] = []
                for name in Cleaned_Judge.split(","):
                    if (name.strip() != ""):
                        advocate_name = {"name": name.strip()}
                        advocate_names_all.append(advocate_name)
                JSON_Data["advocate_names"] = advocate_names_all
                # JSON_Data["date"] = Cleaned_Date_List
                JSON_Data["additional_details"] = []
                JSON_Data["hearing_details"] = []
                JSON_Data["remarks"] = ""
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
                        else:
                            JSON_Data["court_number"] = ""
                JSON_Data["forum"] = "High Court"
                JSON_Data["date"] = today_date
                JSON_Data["state"] = "PNH"
                JSON_Complete_Data.append(JSON_Data)
        # for value in range(len(data)):
        #     for case in range(len(Case_Numbers) -1):
        #         if (value > Case_Numbers[case]['Index'] and value < Case_Numbers[case+1]['Index']):
        #             if (case_regex.search(data[value]['Line_Data']['Value'])):
        #                 Case_Num.append(data[value]['Line_Data']['Value'])
        # with open(Outputlocation + "/" + file_name + "_Batches.txt" ,"w") as f:
        #    for value in Batches:
        #        f.write(str(value))
        # with open(Outputlocation + "/" + file_name + "_Error_logs.txt" ,"w") as f:
        #    for value in Fault_Files:
        #        f.write(str(value) + "\n")


        # df = pd.DataFrame({'Case_Number':Case_Num})
        # df1 = pd.DataFrame({'Party_Names':Party})
        # df2 = pd.DataFrame({'Advocate_Names': Jud_Name})
        # df3 = pd.DataFrame({'Listing_Date': Date_List})
        # #df3 = pd.DataFrame({'Respondent_Adv_Name': Advocate_Names_Respondent})
        # writer = pd.ExcelWriter(Outputlocation + "/" +file_name + ".xlsx")
        # df.to_excel(writer, sheet_name='Sheet1',index=False,startcol=0)
        # df1.to_excel(writer, sheet_name='Sheet1',index=False,startcol=1)                
        # df2.to_excel(writer, sheet_name='Sheet1',index=False,startcol=2)
        # df3.to_excel(writer, sheet_name='Sheet1',index=False,startcol=3)
        # writer.save()
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
            if (value["party_names"].strip() != "") and (len(value["party_names"].strip()) > 10):
                user_collection.insert_one(value)
            #container_client.upsert_item(value)

# inputlocation=input("Please enter the location of JSON : \n")
# Outputlocation=input("Please enter the location of XML : \n")
# list1=[]
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