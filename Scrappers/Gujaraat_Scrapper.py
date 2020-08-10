# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 13:39:19 2020

@author: Vikas Gupta
"""


import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time


today_date = datetime.today().strftime('%d.%m.%Y')
print(today_date)
chrome_options = Options()
download_dir = os.path.join('D:/Scrapping', today_date)
try:
    os.makedirs(download_dir)
except:
    pass

def scrapper(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,  # Change default directory for downloads
    "download.prompt_for_download": False,  # To auto download the file
    })
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)
    
    #driver = webdriver.Chrome(r'C:\Users\Vikas Gupta\Downloads\chromedriver_win32\chromedriver')
    
    driver.get(url)
    
    Cause_List_Element = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[2]/div[2]/div[6]/a")
    
    
    Cause_List_Element.click()
    
    
    go_button_click = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[2]/div[2]/button")
    
    go_button_click.click()
    
    time.sleep(3)
    
    complete_causelist = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[2]/div[5]/div[1]/div/button[5]")
    
    complete_causelist.click()
    
    #ActionChains(driver).click(complete_causelist).perform()
    
    get_causelist_button = driver.find_element_by_xpath("/html/body/div[4]/div[3]/center/div/div[1]/button")
    
    get_causelist_button.click()
    
url = "http://gujarathc-casestatus.nic.in/gujarathc/"

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