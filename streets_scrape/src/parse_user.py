from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from src.cookie_handler import add_cookies
from src.parse_html import parse_page
import argparse
import dotenv

def get_all_information(uid=None, dt=None, page_number=1):
    dotenv.load_dotenv()
    parser = argparse.ArgumentParser(prog="Street Fighter 6 Scraper", 
                            description="This program scrapes information from the buckler website to track street fighter 6 matches")
    
    if uid == None:
        parser.add_argument('-i', '--userid')
        args = parser.parse_args()
        uid = args.userid
        
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


        #Get the matches from the current page and add it to a data frame
        matches = parse_page(driver, "", uid)
    finally:
        driver.quit()
