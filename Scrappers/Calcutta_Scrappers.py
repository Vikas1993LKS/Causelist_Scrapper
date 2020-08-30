# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 17:40:06 2020
@author: Vikas Gupta
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sys
sys.path.append(r'E:\D_Drive\Scrapping\Causelist_Project')
from datetime import datetime
import time
from selenium.webdriver.common.keys import Keys
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Calcutta import parsepdf


def Scrapper(url): 
    today_date = datetime.today().strftime('%d.%m.%Y')
    print(today_date)
    chrome_options = Options()
    download_dir = r'E:\Scrapping\Calcutta\PDF' # + '\/'+  today_date 
    try:
        os.makedirs(download_dir)
    except:
        pass
        
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,  # Change default directory for downloads
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True  # To auto download the file
    }) 
    
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)
    
    driver.get(url)
    
    causelist_elements = driver.find_element_by_xpath("/html/body/div/div[2]/div/div/div")
    for causelist in causelist_elements.find_elements_by_xpath(".//a"):
        for heading_element in causelist.find_elements_by_xpath(".//h5"):
            if (today_date in heading_element.text):
                pdf_element = causelist.get_attribute("href")
                driver.get(pdf_element)
    return download_dir
                

url = "https://www.calcuttahighcourt.gov.in/Notices/CL"

list1 = []

list2 = []

def PDFLocation(pathofPDF):
    for dirpath, dirname, filenames in os.walk(pathofPDF):
        for file in filenames:
            try:
                if file.lower().endswith(".pdf"):
                    path = os.path.abspath(os.path.join(dirpath, file))
                    list1.append(path)
                else:
                    continue
            except (FileNotFoundError, IOError):
                print("runtime exception")
    return list1

def jsonread(pathofjson):
    for dirpath, dirname, filenames in os.walk(pathofjson):
        for file in filenames:
            try:
                if file.lower().endswith(".json"):
                    path = os.path.abspath(os.path.join(dirpath, file))
                    list2.append(path)
                else:
                    continue
            except (FileNotFoundError, IOError):
                print("runtime exception")
    return list2

download_dir = Scrapper(url)

time.sleep(15)

pdf_list = PDFLocation(download_dir)

json_list = jsonread(download_dir)

for file in pdf_list:
    parsepdf(parseFiles(file, download_dir), download_dir)
    
