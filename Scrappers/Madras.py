# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 12:29:58 2020

@author: Vikas Gupta
"""

import os
from selenium import webdriver
import sys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
sys.path.append(r'D:\Scrapping\Scrapping\Causelist_Project')
from datetime import datetime
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Madras import parsepdf
import time
import sys
from selenium.webdriver.common.keys import Keys


#driver = webdriver.Chrome(ChromeDriverManager().install())

today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)
chrome_options = Options()
download_dir = r'D:\Scrapping\Madras\PDF' # + '\/'+  today_date 
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
    
    Daily_causelist_element = driver.find_element_by_xpath('/html/body/form/div/div[1]/input[@value = "DAILY LIST"]')
    
    Daily_causelist_element.click()
    
    Submit_button = driver.find_element_by_xpath("/html/body/form/div/div[7]/div/input[2][@type = 'submit']")
    
    Submit_button.click()
    
    Entire_list_causelist = driver.find_element_by_xpath("/html/body/b/form/table/tbody/tr[2]/td[2]/input[@value = 'ENTIRE LIST']")
    
    Entire_list_causelist.click()
    
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + Keys.RETURN + "2")
        
    window_after = driver.window_handles[1]
        
    time.sleep(3)
        
    driver.switch_to.window(window_after)

url = "http://clists.nic.in/viewlist/index.php?court=U0dsbmFDQkRiM1Z5ZENCdlppQktkV1JwWTJGMGRYSmxJR0YwSUUxaFpISmhjdz09&q=TlRoa1pUaGlaV1ZrWXpNeVpHTXhOalEyTnpOak56ZGxNV015TURabVlURT0="

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