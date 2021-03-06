# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 14:09:29 2020

@author: vikas
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import sys
import os
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

#today_date = datetime.today().strftime('%d-%m-%Y')
 
today_date = "07.09.2020"
       
chrome_options = Options()
download_dir = r'D:\Scrapping\Jammu\PDF'
try:
    os.makedirs(download_dir)
except:
    pass

url = "http://jkhighcourt.nic.in/causelistj.php"

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

for causelist in driver.find_elements_by_xpath(".//strong"):
    if ("Entire List" in causelist.text):
        causelist_element = causelist.find_element_by_xpath(".//a").get_attribute("href")
        print (causelist_element)
        driver.get(causelist_element)
        break