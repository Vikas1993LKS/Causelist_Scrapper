# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 17:07:27 2020

@author: Vikas Gupta
"""


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os
import sys
sys.path.append(r'E:\D_Drive\Scrapping\Causelist_Project')
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Guwahati import parsepdf
import time


today_date = datetime.today().strftime('%d/%m/%Y')
print(today_date)
chrome_options = Options()
download_dir = r'E:\Scrapping\Guwahati\PDF'
try:
    os.makedirs(download_dir)
except:
    pass


def Scrapper(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,  # Change default directory for downloads
    "download.prompt_for_download": False,  # To auto download the file
    })
    
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)
    
    driver.get(url)
    
    Causelist_Table = driver.find_element_by_xpath("/html/body/table[3]")
    
    for row in Causelist_Table.find_elements_by_xpath(".//tr"):
        for value in row.find_elements_by_xpath(".//td"):
            for pdf in value.find_elements_by_xpath(".//a"):
                if (pdf.text == today_date):
                    pdf_element = pdf.get_attribute("href")
                    driver.get(pdf_element)
                    
url = "http://ghconline.nic.in/NewClist.html"

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

Scrapper(url)

time.sleep(15)

pdf_list = PDFLocation(download_dir)

json_list = jsonread(download_dir)

for file in pdf_list:
    parsepdf(parseFiles(file, download_dir), download_dir)
    

for file in pdf_list:
    parsepdf(parseFiles(file, download_dir), download_dir)