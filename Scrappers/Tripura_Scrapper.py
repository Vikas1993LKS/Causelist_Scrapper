# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 17:53:52 2020

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
import time
from Parsers.PDF_Parser_Tripura import parsepdf
from Segmentation.Segmentation_code import parseFiles

today_date = datetime.today().strftime('%d-%m-%Y')

chrome_options = Options()
download_dir = "E:\Scrapping\Tripura\PDF"
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
    
    date_element = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/table/tbody/tr[3]/td/input[1]")
    
    date_element.send_keys(today_date)
    
    Go_element = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/table/tbody/tr[3]/td/input[2]")
    
    Go_element.click()
    
    time.sleep(4)
    
    table_element_causelist = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/div[2]/table")
    
    PDF_links = []
    
    for row in table_element_causelist.find_elements_by_xpath(".//tr"):
        for value in row.find_elements_by_xpath(".//td"):
            for pdf in value.find_elements_by_xpath(".//a"):
                url_link = pdf.get_attribute("href")
                PDF_links.append(url_link)
                # print (url_link)
                # driver.get(url_link)
                # time.sleep(7)
    
    Count = 1
    for link in PDF_links:
        print (link)
        driver.get(link)
        time.sleep(4)
        os.rename(os.path.join(download_dir, "display_causelist.pdf"), os.path.join(download_dir, "display_causelist_" + str(Count) + ".pdf"))
        Count += 1
        
url = "https://services.ecourts.gov.in/ecourtindiaHC/cases/highcourt_causelist.php?state_cd=20&dist_cd=1&court_code=1&stateNm=Tripura"


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