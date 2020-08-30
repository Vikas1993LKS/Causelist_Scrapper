# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 09:17:10 2020

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
from Parsers.PDF_Parser_Delhi import parsepdf
import time


def Scrapper(url):        
    today_date = datetime.today().strftime('%d.%m.%Y')
    print(today_date)
    chrome_options = Options()
    download_dir = r'E:\Scrapping\Delhi\PDF'
    try:
        os.makedirs(download_dir)
    except:
        pass
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
    ul_list = driver.find_elements(By.XPATH, "//*[@id='InnerPageContent']/ul/li")
    count = 1
    for li in ul_list:
        if today_date in li.text:
            pdf_url = li.find_element_by_xpath("//*[@id='InnerPageContent']/ul/li"+'['+str(count)+']'+"/span[2]/a")\
                          .get_attribute('href')
            driver.get(pdf_url)
            count += 1
    return download_dir
    # parseFiles(PDFLocation(download_dir))
            
list1 = []

list2 = []

url = 'http://delhihighcourt.nic.in/causelist_nic_pdf.asp'

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
    print (file)
    parsepdf(parseFiles(file, download_dir), download_dir)
    
