from selenium.webdriver.common.by import By
import time
import random
from cookie_handler import close_cookies
import sqlite3
import pandas as pd
from helper_functions import extract_numbers_regex, get_rank, insert_uid_if_not_exists, get_control_type, get_match_result, check_if_replay_exists

def parse_users(driver, match_div, conn, dt):
    p1_css_selector_dict = {
        "username": ".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1) > span:nth-child(2)",
        "rank": ".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > span:nth-child(1) > img:nth-child(2)",
        "id": ".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1)",
        "character":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "lp_mr":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(3)",
        "alt_rank":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > p:nth-child(1) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "legend_selector":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > p:nth-child(1) > span:nth-child(2)"
    }
    p2_css_selector_dict = {
        "username":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1) > span:nth-child(2)",
        "rank":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > span:nth-child(1) > img:nth-child(2)",
        "id":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1)",
        "character":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "lp_mr":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(3)",
        "alt_rank":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > p:nth-child(1) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "legend_selector":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > p:nth-child(1) > span:nth-child(2)"
    }

    for selector_dict in [p1_css_selector_dict, p2_css_selector_dict]:
        user_dict = {"occurence_dt":dt}

        name = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("username")).text
        user_dict["username"] = name

        id = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("id"))
        user_dict["user_id"] = id.get_attribute("href").split("/")[-1]

        #Also pass connection or cursor
        insert_uid_if_not_exists(user_dict["user_id"], conn)

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
        

        df = pd.DataFrame([user_dict])
        df.to_sql("Users", conn, if_exists="append", index=False)


def parse_match_contestants(driver, match_div, conn, replay_id):
    #replay_id
    #user id
    #character name
    #control type
    #result
    p1_css_selector_dict = {
        "side":"p1",
        "result":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(2) > span:nth-child(2)",
        "character":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "id": ".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1)",
        "control_type":".battle_data_modal__inner___s_ZZ > div:nth-child(2) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(1) > span:nth-child(1) > img:nth-child(2)"
    }
    p2_css_selector_dict = {
        "side":"p2",
        "result":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(2) > span:nth-child(2)",
        "character":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(2) > span:nth-child(1) > span:nth-child(1) > img:nth-child(2)",
        "id":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > p:nth-child(2) > a:nth-child(1)",
        "control_type":".battle_data_modal__inner___s_ZZ > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(1) > span:nth-child(1) > img:nth-child(2)"
    }

    for selector_dict in [p1_css_selector_dict, p2_css_selector_dict]:
        contestant_info = {"Replay_ID": replay_id}

        contestant_info["side"] = selector_dict.get("side")

        result = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("result"))
        contestant_info["result"] = result.text

        character = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("character"))
        contestant_info["character"] = character.get_attribute("alt")

        id = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("id"))
        contestant_info["user_id"] = id.get_attribute("href").split("/")[-1]

        control_type = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("control_type"))
        control_type = control_type.get_attribute("src")
        contestant_info["control_type"] = get_control_type(control_type)

        df = pd.DataFrame([contestant_info])
        df.to_sql("Match_Contestants", conn, if_exists="append", index=False)

def parse_rounds(driver, match_div, conn, replay_id):
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
            curr_round = {"replay_id":replay_id, "round_number":round}

            id = match_div.find_element(By.CSS_SELECTOR, selector_dict.get("id"))
            curr_round["user_id"] = id.get_attribute("href").split("/")[-1]

            curr_round["result"] = get_match_result(img)

            rounds.append(curr_round)


    df = pd.DataFrame(rounds)
    df.to_sql("Match_Rounds", conn, if_exists="append", index=False)

def parse_match(driver, match_div, conn):
    header = match_div.find_element(By.CSS_SELECTOR, ".battle_data_header__xW2Ri")
    
    replay_id = header.find_element(By.CSS_SELECTOR, ".battle_data_replay_id__aSkZW")
    replay_id = replay_id.text.split("Replay ID")[-1]

    if check_if_replay_exists(replay_id, conn):
        print("Match already seen...")
        return None, None
    
    views = header.find_element(By.CSS_SELECTOR, "ul.battle_data_date__f1sP6 > li:nth-child(2)")
    views = int(views.text.split("Views")[-1].split("\n")[-1])
    
    match_type = header.find_element(By.CSS_SELECTOR, ".battle_data_place__CNyCJ")
    match_type = match_type.text
    
    date = header.find_element(By.CSS_SELECTOR, "ul.battle_data_date__f1sP6 > li:nth-child(1)")
    date = date.text
    date = pd.to_datetime(date).tz_localize('US/Central').tz_convert('UTC').isoformat()

    record_dict =  {
        "match_type":match_type,
        "replay_id": replay_id,
        "views": views,
        "occurence_dt": date
    }

    # Check if the replay ID exists

    df = pd.DataFrame([record_dict])
    df.to_sql("Matches", conn, if_exists="append", index=False)
    return date, replay_id


def parse_entire_match(list_item, driver):
    time.sleep(random.uniform(1,2))
    close_cookies(driver)
    list_item.click()
    time.sleep(random.uniform(.5, 1))

    #Check if it is available to be clicked

    match_div = driver.find_element(By.CSS_SELECTOR, ".battle_data_modal__AED01")
    
    filepath = "test.db"
    with sqlite3.connect(filepath) as conn:
        try:
            dt, replay_id = parse_match(driver, match_div, conn)
            if replay_id != None:
                parse_users(driver, match_div, conn, dt)
                parse_match_contestants(driver, match_div, conn, replay_id)
                parse_rounds(driver, match_div, conn, replay_id)
                conn.commit()
        except Exception as e:
            print("Error", e)
            conn.rollback()

    time.sleep(random.uniform(1,2))
    close_cookies(driver)
    close_button = driver.find_element(By.CSS_SELECTOR, ".battle_data_close__A74hN")
    close_button.click()

def parse_page(driver):
    #For each li in 
    ul_for_page = driver.find_element(By.CSS_SELECTOR, ".battle_data_battlelog__list__JNDjG")
    li_elements = ul_for_page.find_elements(By.TAG_NAME, "li")
    #Parses each one 10 times... (investigate this)
    for li in range(int(len(li_elements)/10)):
        list_item = li_elements[(li*10)+1]
        parse_entire_match(list_item, driver)