# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 14:14:11 2020

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
download_dir = r'D:\Scrapping\Patna'
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

url = "http://patnahighcourt.gov.in/EntireClist.aspx?CLIST"

driver.get(url)

Date_entry = input("Enter the causelist date in DD-MMM-YYYY format")

Date_selection = driver.find_element_by_xpath("/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/table/tbody/tr[2]/td/table/tbody/tr/td[2]/select")

for option in Date_selection.find_elements_by_xpath(".//option"):
    if (option.text == Date_entry):
        option.click()
        Show_button = driver.find_element_by_xpath("/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/table/tbody/tr[2]/td/table/tbody/tr/td[3]/input")
        Show_button.click()
        time.sleep(4)
        driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + Keys.RETURN + "2")
        current_url = driver.current_url
        driver.get(current_url)
        print (current_url)
        break