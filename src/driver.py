# -*- coding: utf-8 -*-
import os
import sys
import time

from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def init_driver():
    if os.name == 'nt':
        chrome_options = Options()
        chrome_options.add_argument("--credentials_enable_service=false");
        chrome_options.add_argument("--profile.password_manager_enabled=false");

        path_to_chromedriver = "chromedriver.exe"
        driver = webdriver.Chrome(executable_path = path_to_chromedriver, \
                                                chrome_options=chrome_options)
    else:
        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Firefox()
 
    driver.wait = WebDriverWait(driver, 30)
    return driver

def login_linkedin(driver):
    with open("account.txt") as f:
        account = f.read().splitlines()

    usename = driver.wait.until(EC.presence_of_element_located((By.XPATH, \
                                                        "id('login-email')")))
    usename.send_keys(account[0].split(":")[0])
    time.sleep(1)

    password = driver.wait.until(EC.presence_of_element_located((By.XPATH, \
                                                     "id('login-password')")))
    password.send_keys(account[0].split(":")[1])
    time.sleep(1)

    loginButton = driver.wait.until(EC.presence_of_element_located((By.XPATH, \
                                                        "id('login-submit')")))
    loginButton.click()
    time.sleep(2)
    
def check_recruiter(new_recruiter):
    with open("recruiters.txt") as f:
        recruit_list = f.read().splitlines()
        
    if new_recruiter.encode('ascii', 'ignore') in recruit_list:
        return True
    
    return False

def add_new_recruiter(new_recruiter):
    filehan = open("recruiters.txt", "a")
    filehan.write("%s\n" % new_recruiter.encode('ascii', 'ignore'))
    filehan.close()
        
def find_recruiters(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    recruiters = driver.find_elements_by_xpath("//*[@class='search-result " \
                                   "search-result__occluded-item ember-view']")
    
    for recruiter in recruiters:
        name = recruiter.find_element_by_xpath('.//*[@class="name actor-name"]')
        description = recruiter.find_element_by_xpath('.//*[@class="subline-level-1 Sans-15px-black-85% search-result__truncate"]')

        if check_recruiter("%s-%s? " % (name.text, description.text)):
            continue
        
        button = recruiter.find_element_by_xpath('.//*[@class="ember-view"]')

        if button.text == "Connect":
            add_new_recruiter("%s-%s? " % (name.text, description.text))

            driver.execute_script("return arguments[0].scrollIntoView();", \
                                                                        button)
            driver.execute_script("window.scrollBy(0, -150);")

            sys.stdout.write("Adding %s\n" % name.text)
            button.click()
            time.sleep(1)
             
            addnote = driver.find_element_by_class_name(\
                                            "button-secondary-large")
            addnote.click()
            time.sleep(1)
             
            notes = driver.find_element_by_id("custom-message")
            notes.send_keys("Hello %s,\n\nI have just moved from Houston" \
                            " to San Antonio and would love to" \
                            " hear if you have any opportunities " \
                            "available. Currently I am a software " \
                            "architect at HP, and I'm seeking a " \
                            "software engineer/architect position. " \
                            "\n\nThank you for your time. - Jack" % \
                                                name.text.split(" ")[0])

            sendnote = driver.find_element_by_xpath(\
                            './/*[@class="button-primary-large ml3"]')
            sendnote.click()
            time.sleep(1)

            return True

    return False

if __name__ == "__main__":
    
    driver = init_driver()
    
    # Navigate to home page
    driver.get("http://linkedin.com/")

    # Login to LinkedIn
    login_linkedin(driver)

    # Custom LinkedIn Search
    driver.get("https://www.linkedin.com/search/results/people/?facetGeoRegi" \
               "on=%5B%22us%3A724%22%5D&facetNetwork=%5B%22F%22%2C%22S%22%5D" \
               "&keywords=recruiter&origin=FACETED_SEARCH")
    time.sleep(2)

    # Find recruiters
    while(1):
        if find_recruiters(driver):
            driver.refresh()
            continue
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        nextButton = driver.find_element_by_class_name("next")
        nextButton.click()
        time.sleep(2)

    driver.quit()
