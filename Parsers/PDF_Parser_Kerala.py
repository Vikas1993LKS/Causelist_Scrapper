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


regexp = re.compile(r'^([0-9])')
case_regex = re.compile(r'(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
case_regex_2nd = re.compile(r'^([0-9](\)|.)).+?(((of|OF|\/|-)(\s)?[0-9]{4})(\s)?(\([-a-zA-Z0-9\s]+\)$)?)')
date_regex_acceptance = re.compile(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
date_regex = re.compile(r'(((\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)(19|20)?\d{2}))(\.)?)|(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+)?(,)?(\d{1,2})?(st|nd|th|rd|TH)?(,)?(\s+)?(\d{4})(\.)?|(\d{1,2})(st|nd|th|rd)?(\s+|-)?(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|Feburary|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|AUG|SEPT|OCT|NOV|DEC)(\s+|-)?(,)?(\s+)?(\d{4})(\.)?')
page_number_rejection = re.compile(r'^([0-9]{1,2})(\/)([0-9]{1,2})$')

def parsepdf(data, download_dir):
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
                        if (case_regex.search(data[index]['Line_Data']['Value']) or case_regex_2nd.search(data[index]['Line_Data']['Value'])) and not(date_regex.search(data[index]['Line_Data']['Value'])) and "file" not in data[index]['Line_Data']['Value'] and data[index]['Line_Data']['leftpoint_x'] < 160:
                            Case_Numb.append(data[index]['Line_Data']['Value'].strip())
                        else:
                            pass
                    if (index > Index_1 and index < Index_2) and not(case_regex.search(data[index]['Line_Data']['Value'])) and "VKJNGT+CourierNew,Bold" not in data[index]['Line_Data']['font_name'] and len(data[index]['Line_Data']['Value']) < 70 and not(date_regex.search(data[index]['Line_Data']['Value'])) and not(page_number_rejection.search(data[index]['Line_Data']['Value'].strip().replace("\n",""))) and data[index]['Line_Data']['leftpoint_x'] > Case_Numbers[values]['Left_Point'] and data[index]['Line_Data']['leftpoint_x'] > 100 and "HON'BLE" not in data[index]['Line_Data']['Value'] and "file" not in data[index]['Line_Data']['Value'] and "admission" not in data[index]['Line_Data']['Value'].lower() and "hearing" not in data[index]['Line_Data']['Value'].lower() and "order" not in data[index]['Line_Data']['Value'].lower() and "part" not in data[index]['Line_Data']['Value'].lower() and " pm" not in data[index]['Line_Data']['Value'].lower() and " court" not in data[index]['Line_Data']['Value'].lower() and data[index]['Line_Data']['leftpoint_x'] > 150:
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
                                Judge_Name.append(Batch[ind]['Line_Data']['Value'])
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x']
                            else:
                                Count+=1
                                if(Batch[ind]['Line_Data']['Value'] not in Judge_Name) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 300:
                                        Judge_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                                else:
                                    pass
                        elif (Count == 2):
                            if (Batch[ind]['Line_Data']['leftpoint_x'] == Batch[ind+1]['Line_Data']['leftpoint_x']):
                                Adv_Name.append(Batch[ind]['Line_Data']['Value'].strip())
                                Left_point = Batch[ind]['Line_Data']['leftpoint_x'] 
                            else:
                                Count+=1
                    elif (ind == len(Batch) - 1) and 200 > Batch[ind]['Line_Data']['leftpoint_x'] > 130:
                        Party_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 400 > Batch[ind]['Line_Data']['leftpoint_x'] > 290:
                        Judge_Name.append(Batch[ind]['Line_Data']['Value'].replace("\xa0",""))
                    elif (ind == len(Batch) - 1) and 500 > Batch[ind]['Line_Data']['leftpoint_x'] > 400:
                        Adv_Name.append(Batch[ind]['Line_Data']['Value'].strip().replace("\xa0",""))
                Cleaned_Case_Numbers = ", ".join(Case_Numb)
                Cleaned_Judge = " ".join(Judge_Name)
                Cleaned_Party = " ".join(Party_Name)
                Cleaned_Adv_Name = " ".join(Adv_Name)
                if len(Case_Numb) != 0:
                    if (len(Party_Name) == 0):
                        Fault_Files.append("For the case_number {}, the Party name is not captured".format(Case_Numb[0]))
                    if " vs" not in Cleaned_Party.lower().replace("\n","") and "V/S" not in Cleaned_Party.replace("\n",""):
                        print (Cleaned_Party.replace("\n",""))
                        Fault_Files.append("For the case_number {}, the Party name may be incorrect".format(Case_Numb[0]))
                    if (len(Judge_Name) == 0):
                        Fault_Files.append("For the case_number {}, the Advocate name is not captured".format(Case_Numb[0]))
                else:
                    pass
                Party.append(Cleaned_Party.replace("\n",""))
                Jud_Name.append(Cleaned_Judge.replace("\n",""))
                Case_Num.append(Cleaned_Case_Numbers)
                Advocate_Names_Respondent.append(Cleaned_Adv_Name)
                Batches.append(Batch)
                JSON_Data = {"case_numbers": Cleaned_Case_Numbers}
                JSON_Data["party_name"] = Cleaned_Party.replace("\n", "")
                if ("/") in Cleaned_Judge:
                    JSON_Data["petitioner_advocate_name"] = Cleaned_Judge.replace("\n",",").split("/")[0].strip()
                    JSON_Data["respondent_advocate_name"] = Cleaned_Judge.replace("\n",",").split("/")[1].strip()
                else:
                    JSON_Data["petitioner_advocate_name"] = Cleaned_Judge.replace("\n",",").strip()
                JSON_Data["state"] = "Kerala"
                JSON_Complete_Data.append(JSON_Data)
            elif (values == len(Case_Numbers) - 1):
                Index_Number = Case_Numbers[values]
                for value in range(len(data)):
                    if value >= Index_Number['Index'] and value <= (Index_Number['Index'] + 10):
                        if data[value]['Line_Data']['leftpoint_x'] < 100 and (case_regex_2nd.search(data[value]['Line_Data']['Value']) or (case_regex.search(data[value]['Line_Data']['Value']))):
                            Case_Numb.append(data[value]['Line_Data']['Value'].strip())
                        elif (100 < data[value]['Line_Data']['leftpoint_x'] < 250 and not(date_regex.search(data[value]['Line_Data']['Value']))):
                            Party_Name.append(data[value]['Line_Data']['Value'].strip())
                        elif (250 < data[value]['Line_Data']['leftpoint_x'] < 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
                            Judge_Name.append(data[value]['Line_Data']['Value'].strip())
                        elif (data[value]['Line_Data']['leftpoint_x'] > 400 and not(date_regex.search(data[value]['Line_Data']['Value']))):
                            Adv_Name.append(data[value]['Line_Data']['Value'].strip())
                        else:
                            pass
                Cleaned_Case_Numbers = ", ".join(Case_Numb)
                Cleaned_Judge = " ".join(Judge_Name)
                Cleaned_Party = " ".join(Party_Name)
                Cleaned_Adv_Name = " ".join(Adv_Name)
                #Cleaned_Date_List = ", ".join(Datelist)
                Party.append(Cleaned_Party.replace("\n",""))
                Jud_Name.append(Cleaned_Judge.replace("\n",""))
                #Date_List.append(Cleaned_Date_List.replace("\n",""))
                Case_Num.append(Cleaned_Case_Numbers)
                Advocate_Names_Respondent.append(Cleaned_Adv_Name)
                JSON_Data = {"case_numbers": Cleaned_Case_Numbers}
                JSON_Data["party_name"] = Cleaned_Party.replace("\n", "")
                if ("/") in Cleaned_Judge:
                    JSON_Data["petitioner_advocate_name"] = Cleaned_Judge.replace("\n",",").split("/")[0].strip()
                    JSON_Data["respondent_advocate_name"] = Cleaned_Judge.replace("\n",",").split("/")[1].strip()
                else:
                    JSON_Data["petitioner_advocate_name"] = Cleaned_Judge.replace("\n",",").strip()                
                JSON_Data["state"] = "Kerala"
                JSON_Complete_Data.append(JSON_Data)
#         with open(Outputlocation + "/" + file_name + "_Batches.txt" ,"w") as f:
#            for value in Batches:
#                f.write(str(value))
#         if (len(Fault_Files) != 0):
#             with open(Outputlocation + "/" + file_name + "_Error_logs.txt" ,"w") as f:
#                for value in Fault_Files:
#                    f.write(str(value) + "\n")


#         df = pd.DataFrame({'Case_Number':Case_Num})
#         df1 = pd.DataFrame({'Party_Names':Party})
#         df2 = pd.DataFrame({'Advocate_Names': Jud_Name})
#         #df3 = pd.DataFrame({'Listing_Date': Date_List})
#         df3 = pd.DataFrame({'Respondent_Adv_Name': Advocate_Names_Respondent})
#         writer = pd.ExcelWriter(Outputlocation + "/" +file_name + ".xlsx")
#         df.to_excel(writer, sheet_name='Sheet1',index=False,startcol=0)
#         df1.to_excel(writer, sheet_name='Sheet1',index=False,startcol=1)                
#         df2.to_excel(writer, sheet_name='Sheet1',index=False,startcol=2)
#         df3.to_excel(writer, sheet_name='Sheet1',index=False,startcol=3)
#         writer.save()
        print (JSON_Complete_Data)

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