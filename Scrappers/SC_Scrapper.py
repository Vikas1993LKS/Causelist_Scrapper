# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 12:06:46 2020

@author: Vikas Gupta
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import sys
sys.path.append(r'E:\D_Drive\Scrapping\Causelist_Project')
import os
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_SC import parsepdf
import time


today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)
chrome_options = Options()
download_dir = r'E:\Scrapping\SC\PDF'
try:
    os.makedirs(download_dir)
except:
    pass

def scrapper(url):
    today_date = datetime.today().strftime('%d-%m-%Y')
    print(today_date)
    chrome_options = Options()
    download_dir = r'E:\Scrapping\SC\PDF'
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
    
    Causelist_Table = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div/div/div[2]/table")
    
    for row in Causelist_Table.find_elements_by_xpath(".//tr"):
        for value in row.find_elements_by_xpath(".//td"):
            for centre in value.find_elements_by_xpath(".//center"):
                if (centre.text == today_date):
                    for pdf_element in centre.find_elements_by_xpath(".//a"):
                        pdf_link = pdf_element.get_attribute("href")
                        time.sleep(4)
                        driver.get(pdf_link)
    return download_dir

list1 = []

list2 = []

url = "https://main.sci.gov.in/causelist"

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

download_dir = scrapper(url)

time.sleep(15)

pdf_list = PDFLocation(download_dir)

json_list = jsonread(download_dir)

for file in pdf_list:
    parsepdf(parseFiles(file, download_dir), download_dir)