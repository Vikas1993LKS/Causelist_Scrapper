# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 16:03:46 2020

@author: Vikas.gupta
"""

import pandas as pd
import json
import os 
import re
import xml.etree.cElementTree as ET
from nltk.stem import PorterStemmer
# from flair.models import SequenceTagger
# from flair.data import Sentence
# tagger = SequenceTagger.load('ner-ontonotes-fast')
import pickle

Month = {("January","JANUARY","JAN","Jan"): '01', ("February","FEBRUARY","FEBURARY","Feburary","Feb","FEB"): '02',("March","MARCH","Mar","MAR"): '03',("April","APRIL","Apr","APR"): '04',("May","MAY"): '05', ("June","JUNE","JUN","Jun"): '06',("July","JULY","Jul","JUL"): '07', ("August","AUGUST","Aug","AUG"): '08',("September","SEPTEMBER","SEPT","Sept","SEPT"): '09',("October","OCTOBER","OCT","OCT"):'10',("November","NOVEMBER","Nov","NOV"): '11',("December","DECEMBER","DEC","Dec"): '12'}
# dataset = pd.read_csv(r'D:\Scrapping\Scrapping\Causelist_Project\Causelist_Metadata\pandas_simple_modified_revision_1.tsv', delimiter = '\t', quoting = 3)
# y = dataset['Label']


pdf_filename=[]
Judgement_Date_List = []

def metadata_extractor(data):
    Metadata_details_judge_name =[]
    Metadata_details_court_number = []
    datasets_value = []
    #print (data)
    if (len(data) == 0):
        pass
    else:
        for i in range(len(data)):
            datasets_value.append(data[i]['Line_Data']['Value'])
    X_test_1= list(datasets_value)         
    for i in range(len(data)):
            str_court_number = ""
            str_Judgename = ""
            for key in data[i]:
                if len(X_test_1[i].strip()) <= 60 and data[i]['Line_Data']['leftpoint_x'] > 100 and "bold" in data[i]['Line_Data']['font_name'].lower() and (('JUSTICE' in X_test_1[i]) or ('Justice' in X_test_1[i])) and ("HON'BLE" in X_test_1[i] or "HONOURABLE" in X_test_1[i]) and "order" not in X_test_1[i].lower():
                    str_Judgename = X_test_1[i].replace('(Oral)','').replace('(oral)','').replace('(ORAL)','').replace('(','').replace(')','').strip()+"\n"
                    MetaData_Judge_Name = {"judge_name" : str_Judgename, "Index": i}
                    Metadata_details_judge_name.append(MetaData_Judge_Name)
                elif ("court no" in X_test_1[i].strip().lower() or "CR NO " in X_test_1[i].strip() or "court hall" in X_test_1[i].strip().lower() or "room no." in X_test_1[i].strip().lower()):
                    str_court_number = X_test_1[i]
                    MetaData_Court_Number = {"court_number" : str_court_number, "Index": i}
                    Metadata_details_court_number.append(MetaData_Court_Number)
                else:
                    pass
    if (len(Metadata_details_judge_name) == 0):
            for i in range(len(data)):
                str_court_number = ""
                str_Judgename = ""
                for key in data[i]:
                    if len(X_test_1[i].strip()) <= 60 and (('JUSTICE' in X_test_1[i]) or ('Justice' in X_test_1[i])) and ("HON'BLE" in X_test_1[i] or "HONOURABLE" in X_test_1[i]) and "order" not in X_test_1[i].lower():
                        str_Judgename = X_test_1[i].replace('(Oral)','').replace('(oral)','').replace('(ORAL)','').replace('(','').replace(')','').strip()+"\n"
                        MetaData_Judge_Name = {"judge_name" : str_Judgename, "Index": i}
                        Metadata_details_judge_name.append(MetaData_Judge_Name)
                    elif ("court no." in X_test_1[i].strip().lower() or "CR NO " in X_test_1[i].strip() or "court hall" in X_test_1[i].strip().lower() or "room no." in X_test_1[i].strip().lower()):
                        str_court_number = X_test_1[i]
                        MetaData_Court_Number = {"court_number" : str_court_number, "Index": i}
                        Metadata_details_court_number.append(MetaData_Court_Number)
                    else:
                        pass
    Judge_Names = []
    Judge_Name_Details = []
    if (len(Metadata_details_judge_name) == 1):
        Judge_Names.append(MetaData_Judge_Name['judge_name'])
        Judge_Details = {"judge_name" : Judge_Names, "Index" : MetaData_Judge_Name['Index']}
        Judge_Name_Details.append(Judge_Details)
    else:
        for value in range(len(Metadata_details_judge_name)):
            if (value < len(Metadata_details_judge_name) - 1):
                if (Metadata_details_judge_name[value + 1]['Index'] - Metadata_details_judge_name[value]['Index'] < 2):
                    Judge_Names.append(Metadata_details_judge_name[value]['judge_name'])
                else:
                    #Judge_Name.append(Metadata_details_judge_name[value + 1]['judge_name'])
                    Judge_Names.append(Metadata_details_judge_name[value]['judge_name'])
                    Judge_Details = {"judge_name" : Judge_Names, "Index" : Metadata_details_judge_name[value]['Index']}
                    Judge_Name_Details.append(Judge_Details)
                    Judge_Names = []
            elif (value == len(Metadata_details_judge_name) -1) and (Metadata_details_judge_name[value]['Index'] - Metadata_details_judge_name[value - 1]['Index'] < 2) :
                Judge_Names.append(Metadata_details_judge_name[value]['judge_name'])
                Judge_Details = {"judge_name" : Judge_Names, "Index" : Metadata_details_judge_name[value]['Index']}
                Judge_Name_Details.append(Judge_Details)
                Judge_Names = []
    return (Judge_Name_Details, Metadata_details_court_number)