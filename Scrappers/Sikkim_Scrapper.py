# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 13:45:57 2020

@author: Vikas Gupta
"""


import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
from selenium.webdriver.common.keys import Keys

today_date = datetime.today().strftime('%d-%m-%Y')
print(today_date)

chrome_options = Options()
download_dir = r'D:\Scrapping\Sikkim'
try:
    os.makedirs(download_dir)
except:
    pass

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

URL = "https://hcs.gov.in/hcs/"

driver.get(URL)

Causelist_element = driver.find_element_by_xpath("/html/body/div/div[5]/div/div[2]/div/div[1]/div[2]/p/a")

Causelist_element.click()

time.sleep(3)

Causelist_Table = driver.find_element_by_xpath("/html/body/div/div[7]/div/div/div/table")

for row in Causelist_Table.find_elements_by_xpath(".//tr[1]"):
    for pdf_element in row.find_elements_by_xpath(".//a"):
        if (pdf_element.get_attribute("href")):
            pdf_link = pdf_element.get_attribute("href")
            print (pdf_link)
            time.sleep(5)
            driver.get(pdf_link)
            break