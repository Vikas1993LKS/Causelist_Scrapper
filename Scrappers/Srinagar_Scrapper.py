# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 14:09:29 2020

@author: vikas
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
import sys
import os
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def Reverse(lst): 
    return [ele for ele in reversed(lst)] 

today_date = ".".join(Reverse(str(datetime.date.today() + datetime.timedelta(1)).split("-")))

print (today_date)
# today_date = datetime.strftime('%d.%m.%Y')
        
chrome_options = Options()
download_dir = r'E:\Scrapping\Srinagar\PDF'
try:
    os.makedirs(download_dir)
except:
    pass

url = "http://jkhighcourt.nic.in/causelistk.php"

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

for element in driver.find_elements_by_xpath(".//strong"):
    if ("Entire List" in element.text):
        pdf_url = element.find_element_by_xpath(".//a").get_attribute("href")
        driver.get(pdf_url)
        break