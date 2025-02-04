from selenium.webdriver.common.by import By
import time
import os
import dotenv
import random
from src.cookie_handler import close_cookies
from pprint import pprint
import pandas as pd
from src.helper_functions import *

def parse_users(driver, match_div, dt):
    p1_css_selector_dict = {
        "username": ".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1) > span:nth-child(2)",
        "rank": ".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > span:nth-child(1) > img:nth-child(2)",
        "id": ".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1)",
        "character":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "lp_mr":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(3)",
        "alt_rank":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > p:nth-child(1) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "legend_selector":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > p:nth-child(1) > span:nth-child(2)",
        "side":"p1",
        "result":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(2) > span:nth-child(2)",
        "character":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "control_type":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(1) > span:nth-child(1) > img:nth-child(2)"
    
    }
    p2_css_selector_dict = {
        "username":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1) > span:nth-child(2)",
        "rank":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > span:nth-child(1) > img:nth-child(2)",
        "id":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1)",
        "character":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "lp_mr":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(3)",
        "alt_rank":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > p:nth-child(1) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "legend_selector":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > p:nth-child(1) > span:nth-child(2)",
        "side":"p2",
        "result":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(2) > span:nth-child(2)",
        "character":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "control_type":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(1) > span:nth-child(1) > img:nth-child(2)"
    }

    users = []

    for selector_dict in [p1_css_selector_dict, p2_css_selector_dict]:
        user_dict = {"occurence_dt":dt}

        name = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("username")).text
        user_dict["username"] = name

        id = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("id"))
        user_dict["user_id"] = id.get_attribute("href").split("/")[-1]

        character = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("character"))
        user_dict["character"] = character.get_attribute("alt")

        lp = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("lp_mr"))
        lp = lp.text
        val = extract_numbers_regex(lp)
        lp_mr = dict()
        if "LP" in lp:
            lp_mr = {"LP":val, "MR":None}
        if "MR" in lp:
            lp_mr = {"LP": None, "MR":val}
        user_dict.update(lp_mr)

        #May be wrong on legend ranks
        if len(match_div.find_elements(By.CSS_SELECTOR, selector_dict.get("rank"))) > 0:    
            rank = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("rank"))
            rank = rank.get_attribute("src")
            rank = get_rank(rank, match_div, driver)
        elif len(match_div.find_elements(By.CSS_SELECTOR, selector_dict.get("alt_rank"))) >0:
            rank = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("alt_rank"))
            rank = rank.get_attribute("src")
            legend_selector = selector_dict.get("legend_selector")
            rank = get_rank(rank, match_div, driver, legend_selector)
        else:
            print("NO RANK FOUND")
            rank = ""

        user_dict["rank"] = rank

        user_dict["side"] = selector_dict.get("side")

        result = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("result"))
        user_dict["result"] = result.text

        character = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("character"))
        user_dict["character"] = character.get_attribute("alt")

        control_type = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("control_type"))
        control_type = control_type.get_attribute("src")
        user_dict["control_type"] = get_control_type(control_type)

        users.append(user_dict)

    return users

    

def parse_rounds(driver, match_div, replay_id):
    p1_css_selector_dict = {
        "id":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1)",
        "round_list":".battle_data_match_player1__yK_cd"
    }
    p2_css_selector_dict = {
        "id":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1)",
        "round_list":".battle_data_match_player2__hRDv4"
    }
    rounds = []

    for selector_dict in [p1_css_selector_dict, p2_css_selector_dict]:
        p2_results = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("round_list"))
        matches = p2_results.find_elements(By.TAG_NAME, "img")
        for round, img in enumerate(matches, 1):
            curr_round = {"round_number":round}

            id = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("id"))
            curr_round["user_id"] = id.get_attribute("href").split("/")[-1]

            curr_round["result"] = get_match_result(img)

            if curr_round["result"] != "Loss":
                rounds.append(curr_round)
    
    return rounds

def parse_match(driver, match_div, latest_dt, uid):
    header = match_div.find_element(By.CSS_SELECTOR, ".battle_data_header__xW2Ri")
    
    replay_id = header.find_element(By.CSS_SELECTOR, ".battle_data_replay_id__aSkZW")
    replay_id = replay_id.text.split("Replay ID")[-1]

    date = header.find_element(By.CSS_SELECTOR, "ul.battle_data_date__f1sP6 > li:nth-child(1)")
    date = date.text
    date = pd.to_datetime(date).tz_localize('US/Central').tz_convert('UTC').isoformat()

    #Check if it's past time, check if it already exists...

    views = header.find_element(By.CSS_SELECTOR, "ul.battle_data_date__f1sP6 > li:nth-child(2)")
    views = int(views.text.split("Views")[-1].split("\n")[-1])
    
    match_type = header.find_element(By.CSS_SELECTOR, ".battle_data_place__CNyCJ")
    match_type = match_type.text

    record_dict =  {
        "match_type":match_type,
        "replay_id": replay_id,
        "views": views,
        "occurence_dt": date
    }

    return date, replay_id, record_dict


def parse_entire_match(list_item, driver, latest_dt, uid):
    time.sleep(random.uniform(1,2))
    close_cookies(driver)
    list_item.click()
    time.sleep(random.uniform(.5, 1))

    #Check if it is available to be clicked?

    match_div = driver.find_element(By.CSS_SELECTOR, ".battle_data_modal__AED01")
    
    dotenv.load_dotenv()
    try:
        dt, replay_id, match_dict = parse_match(driver, match_div, latest_dt, uid)
        #None was a way of signifying that it was already done
        if replay_id != None:
            #Merge these two
            contestants = parse_users(driver, match_div, dt)
            
            match_dict["Contestants"] = contestants
            #Rounds
            rounds = parse_rounds(driver, match_div, replay_id)
            match_dict["Rounds"] = rounds
            pprint(match_dict)
            print("Added match successfully!")
    except Exception as e:
        print("Error", e)

    time.sleep(random.uniform(1,2))
    close_cookies(driver)
    close_button = driver.find_element(By.CSS_SELECTOR, ".battle_data_close__A74hN")
    close_button.click()

    return match_dict

def parse_page(driver, latest_dt, uid):
    #For each li in 
    ul_for_page = driver.find_element(By.CSS_SELECTOR, ".battle_data_battlelog__list__JNDjG")
    li_elements = ul_for_page.find_elements(By.TAG_NAME, "li")
    #Parses each one 10 times... (investigate this)
    matches = []
    for li in range(int(len(li_elements)/10)):
        list_item = li_elements[(li*10)+1]
        match_dict = parse_entire_match(list_item, driver, latest_dt, uid)
        matches.append(match_dict)
    return matches