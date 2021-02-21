# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 17:16:32 2020

@author: Vikas Gupta
"""


import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys
sys.path.append(r'D:\Scrapping\Scrapping\Causelist_Project')
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Uttarakhand import parsepdf
import time
from selenium.webdriver.common.keys import Keys

today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)

chrome_options = Options()
download_dir = r"D:\Scrapping\Uttarakhand\PDF"
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
    
    Daily_Causelist_Select_Button = driver.find_element_by_xpath("/html/body/form/div/div[2]/input")
    
    Daily_Causelist_Select_Button.click()
    
    Submit_button = driver.find_element_by_xpath("/html/body/form/div/div[3]/div/input[2]")
    
    Submit_button.click()
    
    date_selection = driver.find_element_by_xpath("/html/body/b/form/div/select")
    
    for date in date_selection.find_elements_by_xpath(".//option"):
        if (date.text == "25-08-2020"):
            date.click()
            
    Causelist_PDF = driver.find_element_by_xpath("/html/body/b/form/table/tbody/tr[2]/td/input")
    
    Causelist_PDF.click()
    
    
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + Keys.RETURN + "2")
    
    window_after = driver.window_handles[1]
    time.sleep(5)
    # driver.switch_to.window(window_after)
    driver.switch_to.window(window_after);
# print('window after' ,window_after)
# current_url = driver.current_url
# print('current url' ,current_url)

# #print('element' , element.get_attribute("innerHTML"))
# driver.get(current_url)
    
url = "http://clists.nic.in/viewlist/index.php?court=U0dsbmFDQkRiM1Z5ZENCdlppQlZkSFJoY21GcmFHRnVaQ0JoZENCT1lXbHVhWFJoYkE9PQ==&q=TkdJMFlUazJZV000WW1JNE5XTmpOelUzTnpVeFpXTXlNRFZrWXpVMFkyUT0="

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