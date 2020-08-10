# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 13:22:32 2020

@author: Vikas Gupta
"""


import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys
sys.path.append(r'E:\D_Drive\Scrapping\Causelist_Project')
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Odisha import parsepdf
import time
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
download_dir = r'E:\Scrapping\Odisha\PDF'
try:
    os.makedirs(download_dir)
except:
    pass

def scrapper(url):
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
    
    for row in driver.find_elements_by_xpath(".//tr"):
        Count = 1
        for data in row.find_elements_by_xpath(".//td"):
            if ("Supplementary List") in data.text:
                pdf_element = row.find_element_by_xpath(".//td["+ str(Count+1) +"]/span/a").get_attribute("href")
                time.sleep(3)
            Count += 1
        
    
    new_url = pdf_element    
    
    driver.get(new_url)
    
    body_element = driver.find_element_by_xpath("//*")
    
    pdf_link = body_element.find_element_by_xpath("//object").get_attribute("data")
    
    driver.get(pdf_link)
    
url = "https://orissahighcourt.nic.in/cause-list/"

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

scrapper(url)

time.sleep(15)

pdf_list = PDFLocation(download_dir)

json_list = jsonread(download_dir)

for file in pdf_list:
    parsepdf(parseFiles(file, download_dir), download_dir)