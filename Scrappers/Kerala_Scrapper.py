# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 17:34:18 2020

@author: Vikas Gupta
"""


# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 16:23:50 2020

@author: Vikas Gupta
"""


import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sys
sys.path.append(r'E:\D_Drive\Scrapping\Causelist_Project')
from datetime import datetime
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Kerala import parsepdf
import time
from selenium.webdriver.common.keys import Keys

today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)

chrome_options = Options()
download_dir = r'E:\Scrapping\Kerala\PDF'
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
    
    Date_Selection = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/table/tbody/tr[3]/td/input[1]")
    
    Date_Selection.send_keys(input("Enter the date in dd-mm-yyyy format"))
    
    go_button = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/table/tbody/tr[3]/td/input[2]")
    
    go_button.click()
    
    Causelist_table = driver.find_element_by_xpath("/html/body/form/table/tbody/tr/td/div[2]/table")
    
    pdf_links = []
    
    for pdf_element in Causelist_table.find_elements_by_xpath(".//a"):
        time.sleep(2)
        if (pdf_element.text == "View"):
            pdf_link = pdf_element.get_attribute("href")
            pdf_links.append(pdf_link)
            
    
    Count = 1
    for link in pdf_links:
       try:
           driver.get(link)
           time.sleep(8)
           os.rename(os.path.join(download_dir, "display_causelist.pdf"), os.path.join(download_dir, "display_causelist_" + str(Count) + ".pdf"))
           Count += 1
       except:
           pass
       
url = "https://services.ecourts.gov.in/ecourtindiaHC/cases/highcourt_causelist.php?state_cd=4&dist_cd=1&court_code=1&stateNm=Kerala"
    
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