from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random
import re
import sqlite3
from cookie_handler import add_cookies
from sql_interaction import sqlite_init
from parse_html import parse_page

import argparse

def get_all_information(id=None):
    parser = argparse.ArgumentParser(prog="Street Fighter 6 Scraper", 
                            description="This program scrapes information from the buckler website to track street fighter 6 matches")
    
    if id == None:
        parser.add_argument('-i', '--userid')
        args = parser.parse_args()
        id = args.userid

    #Get the correct page
    page_number = 1
    webpage = f"https://www.streetfighter.com/6/buckler/profile/{id}/battlelog?page={page_number}"
    try:
        #Start a selenium browser and add cookies
        options = webdriver.FirefoxOptions()
        # options.add_argument("-headless")
        # options.add_argument("--disable-extensions")
        driver = webdriver.Firefox(options=options)
        driver.get(webpage)
        time.sleep(3)

        add_cookies(driver)
        driver.refresh()

        sqlite_init("test.db")

        while True:

            #Get the matches from the current page and add it to a data frame
            parse_page(driver)
            
            #If it is the last page, then break
            page_list = driver.find_element(By.CSS_SELECTOR, ".numberWrap > ul:nth-child(1)")
            pages = page_list.find_elements(By.TAG_NAME, "li")
            last_page = pages[-1]
            classes = last_page.get_attribute("class")
            if "active" in classes.split(" "):
                break

            # Move to the next page
            next_page = driver.find_element(By.CSS_SELECTOR, ".numberWrap > ul:nth-child(1) > li.active + li")
            next_page.click()
            time.sleep(10)
    finally:
        driver.quit()

if __name__ == "__main__":
    get_all_information()
    pass