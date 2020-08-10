# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 13:39:19 2020

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
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Meghalya import parsepdf


today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)
chrome_options = Options()
download_dir = r'E:\Scrapping\Meghalya\PDF'
try:
    os.makedirs(download_dir)
except:
    pass

def Scrapper(url):
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
    
    
    # from selenium import webdriver
    # from selenium.webdriver.common.keys import Keys
    
    # import requests
    
    # import os
    
    # from webdriver_manager.chrome import ChromeDriverManager
    
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    #driver = webdriver.Chrome(r'C:\Users\Vikas Gupta\Downloads\chromedriver_win32\chromedriver')
    
    driver.get(url)
    
    date_search_element = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/table/tbody/tr[3]/td/input[1]")
    
    #date_search_element.send_keys(input("Please_Enter the Causelist Date"))
    
    date_search_element.send_keys(today_date)
    
    go_button_click = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/table/tbody/tr[3]/td/input[2]")
    
    go_button_click.click()
    
    table = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/div[2]/table")
    
    Count = 1
    for row in table.find_elements_by_xpath(".//tr"):
        for value in row.find_elements_by_xpath(".//td"):
            for pdf in value.find_elements_by_xpath(".//a"):
                url_link = pdf.get_attribute("href")
                print (url_link)
                driver.get(url_link)
                time.sleep(5)
                os.rename(os.path.join(download_dir, "display_causelist.pdf"), os.path.join(download_dir, "display_causelist_" + str(Count) + ".pdf"))
                Count += 1
    return download_dir

url = "https://services.ecourts.gov.in/ecourtindiaHC/cases/highcourt_causelist.php?state_cd=21&dist_cd=1&court_code=1&stateNm=Meghalaya"

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