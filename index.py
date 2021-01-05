from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import time
from pathlib import Path

import secrets

''' secrets.py
USER = "user"
PASSWORD = "password"

DOWNLOAD_FOLDER = '/path/to/Download/foklder/'
WEBSITE_TO_SCRAPE = 'https://example.com/'
'''

def clean_download_dir():
    for f in os.listdir(secrets.DOWNLOAD_FOLDER):
        os.remove(os.path.join(secrets.DOWNLOAD_FOLDER,f))

def setup_chromedriver():
    PATH = os.getcwd() + '/chromedriver'
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
            "download.default_directory": secrets.DOWNLOAD_FOLDER,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
    })
    browser = webdriver.Chrome(options=chrome_options, executable_path=PATH)
    return browser

def go_to_homepage(browser):
    browser.get(secrets.WEBSITE_TO_SCRAPE)
    browser.implicitly_wait(10) # seconds

def login(browser):
    user_form = browser.find_element_by_id('j_username')
    user_form.send_keys(secrets.USER)
    pw_form = browser.find_element_by_id('j_password')
    pw_form.send_keys(secrets.PASSWORD)
    pw_form.send_keys(Keys.RETURN)
    browser.implicitly_wait(5)

def select_project(browser):
    browser.find_element_by_css_selector('#listaPratiche').click()
    browser.implicitly_wait(5)

def select_documents(browser):
    browser.find_element_by_css_selector('#menuPratica').click()
    browser.implicitly_wait(10)
    browser.find_element_by_css_selector('#contextMenu > li:nth-child(2)').click()
    browser.implicitly_wait(10)
    browser.find_element_by_css_selector('#funzione28').click()
    browser.find_element_by_css_selector('#ui-id-2').click()
    browser.implicitly_wait(10)

def get_all_documents(browser):
    rows = browser.find_elements_by_css_selector('.zebra')
    browser.implicitly_wait(10)
    return rows

def create_folder_structure(row, row_count):
    folder_name = row.find_element_by_css_selector('.title').text
    if "DOCUMENTI SOLA LETTURA - " in folder_name:
        folder_name = f"{row_count}._{folder_name.split('DOCUMENTI SOLA LETTURA - ')[1]}"
    Path('./download/' + folder_name).mkdir(parents=True, exist_ok=True)
    print(f"{folder_name} (created)")
    return folder_name

def main():
    clean_download_dir()
    browser = setup_chromedriver()
    go_to_homepage(browser)
    login(browser)
    select_project(browser)
    select_documents(browser)
    rows = get_all_documents(browser)
    row_count = 0
    for row in rows[5:]:
        folder_name = create_folder_structure(row, row_count)
        fileList = row.find_elements_by_css_selector('.wide')
        item_count = 0
        for item in fileList:
            fileNames = item.find_elements_by_css_selector('.size-22.font-bold')
            for fileName in fileNames:
                if fileName.text == 'Descrizione documento':
                    pass
                else:
                    item_count += 1
                    print('-> ' + fileName.text)
                    fileButton = item.find_element_by_css_selector('button.download')
                    fileButton.click()
                    time.sleep(10)
                    dl_wait = True
                    seconds = 0
                    while dl_wait and seconds < 100:
                        for fName in os.listdir('/Users/nicolamastrandrea/Downloads/chromedriver/'):
                            if fName.endswith('.crdownload'):
                                dl_wait = True
                            else:
                                dl_wait = False
                                if not os.path.exists(os.path.join(os.getcwd(),"download", folder_name, f"{item_count}._{fileName.text}")):
                                    Path(os.path.join(os.getcwd(),"download", folder_name, f"{item_count}._{fileName.text}")).mkdir(parents=True, exist_ok=True)
                                try:
                                    os.rename(os.path.join(secrets.DOWNLOAD_FOLDER,fName), os.path.join(os.getcwd(),"download", folder_name, f"{item_count}._{fileName.text}", fName))
                                except FileNotFoundError:
                                    print("File " + fName + "Not Found")
                            time.sleep(1)
                            seconds += 1
        row_count += 1
        
main()