# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 19:15:13 2020

@author: Vikas Gupta
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
sys.path.append(r'D:\Scrapping\Scrapping\Causelist_Project')
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from Segmentation.Segmentation_code import parseFiles
from Parsers.PDF_Parser_Chattisgarh import parsepdf
import time
from selenium.webdriver.common.keys import Keys


today_date = datetime.today().strftime('%d.%m.%Y')
today_date
chrome_options = Options()
download_dir = r'D:\Scrapping\Chattisgarh\PDF'
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
    
    # driver = webdriver.Chrome(r'C:\Users\Vikas Gupta\Downloads\chromedriver_win32\chromedriver')
    
    driver.get(url)
    
    Submit_element = driver.find_element_by_xpath("/html/body/form/div/div[9]/div/input[2]")
    
    Submit_element.click()
    
    go_button_click = driver.find_element_by_xpath("/html/body/b/form/table/tbody/tr[2]/td[3]/input")
        
    go_button_click.click()
    
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + Keys.RETURN + "2")
    
    window_after = driver.window_handles[1]
    
    time.sleep(3)
    
    driver.switch_to.window(window_after)

    # current_url = driver.current_url

    # driver.get(current_url)
    
    return download_dir
    
url = "http://clists.nic.in/viewlist/index.php?court=UTJoaGRIUnBjMmRoY21nZ1NHbG5hQ0JEYjNWeWRDQXRJRUpwYkdGemNIVnk=&q=WkdJM1pUQTJZelF3WWpNd09UUTRaVEJoTmpBME5HUTJZVFZoWVRoallqUT0="

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