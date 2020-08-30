# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:20:09 2020

@author: Vikas Gupta
"""


import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import sys
sys.path.append(r'E:\D_Drive\Scrapping\Causelist_Project')
from datetime import datetime
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Punjab import parsepdf
import time
from selenium.webdriver.common.keys import Keys

today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)

chrome_options = Options()
download_dir = r'E:\Scrapping\Punjab\PDF'
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
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)
    
    
    input_date = today_date

    driver.get(url)
    
    Causelist_date = driver.find_element_by_xpath("/html/body/center/table[2]/tbody/tr[2]/td[2]/input").get_attribute("value")
    
    #driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[1]);", Causelist_date, "value", input_date);
    
    View_Causelist = driver.find_element_by_xpath("/html/body/center/table[2]/tbody/tr[4]/td/input")
    
    View_Causelist.click()
    
    table_causelist = driver.find_element_by_xpath("/html/body/center/table")
    
    
    for row in table_causelist.find_elements_by_xpath(".//tr"):
        Count = 1
        for data in row.find_elements_by_xpath(".//td"):
            if ("Complete List") in data.text:
                pdf_element = row.find_element_by_xpath(".//td["+ str(Count) +"]/a")
                pdf_element.click()
                time.sleep(3)
                
    
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + Keys.RETURN + "2")
    window_after = driver.window_handles[1]
    time.sleep(3)
    driver.switch_to.window(window_after)

url = "https://highcourtchd.gov.in/clc.php"

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