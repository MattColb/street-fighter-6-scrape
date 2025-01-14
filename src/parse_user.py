from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from src.cookie_handler import add_cookies
from src.sql_interaction import sqlite_init
from src.parse_html import parse_page
import argparse
import dotenv
from src.helper_functions import get_latest_dt
import os
import sqlite3

def get_all_information(uid=None):
    dotenv.load_dotenv()
    parser = argparse.ArgumentParser(prog="Street Fighter 6 Scraper", 
                            description="This program scrapes information from the buckler website to track street fighter 6 matches")
    
    if uid == None:
        parser.add_argument('-i', '--userid')
        args = parser.parse_args()
        uid = args.userid
        

    
    #Get the correct page
    page_number = 1
    webpage = f"https://www.streetfighter.com/6/buckler/profile/{uid}/battlelog?page={page_number}"
    try:
        #Start a selenium browser and add cookies
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        # options.add_argument("--disable-extensions")
        driver = webdriver.Firefox(options=options)
        driver.get(webpage)
        time.sleep(3)

        add_cookies(driver)
        driver.refresh()

        sqlite_init(os.getenv("DBNAME"))
        conn = sqlite3.connect(os.getenv("DBNAME"))
        latest_dt = get_latest_dt(uid, conn)
        conn.close()


        while True:

            #Get the matches from the current page and add it to a data frame
            parse_page(driver, latest_dt, uid)
            
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
            time.sleep(5)
            driver.refresh()
    finally:
        driver.quit()
