from selenium.webdriver.common.by import By
import re
import pandas as pd
import sqlite3
import os

def get_control_type(control_type_src):
    control_type = control_type_src.split("/")[-1].split(".")[0][-1]
    if control_type == "1":
        return "Modern"
    return "Classic"

def get_rank_stars(rank_number):
    match rank_number%5:
        case 0:
            return 5
        case _:
            return rank_number%5

def get_legend_rank(match, selector, driver):
    #Str has no find_element
    legend_num = match.find_element(By.CSS_SELECTOR, selector)
    return legend_num.text

def extract_numbers_regex(string):
    num = ''.join(re.findall(r'\d+', string))
    if num == "":
        return 0
    return int(num)

rank_dict = {
    0: "Rookie",
    1: "Iron",
    2: "Bronze",
    3: "Silver",
    4: "Gold", 
    5: "Diamond",
    6: "Platinum"
}

match_results = {
    0: "Loss",
    1: "Victory",
    2: "Chipkill",
    3: "Timeout",
    4: "Draw",
    5: "Overdrive",
    6: "Super Art",
    7: "Critical Art",
    8: "Perfect"
}

def get_match_result(img):
    src = img.get_attribute("src")
    src = src.split("/")[-1]
    src = src.split("_")[-2]
    src = src.split("result")[-1]
    src = int(src)
    result = match_results.get(src, "Loss")
    return result

def get_rank(rank, match, driver, selector=None):
    #Processing it out from the src path
    rank = rank.split("/")[-1]
    rank = rank.split("_")[0]
    rank = rank.split("rank")[-1]
    try:
        rank = int(rank)
    except:
        rank = 1
    
    #Handling edge cases
    if rank == 39:
        return "New Challenger"
    if rank == 36:
        return "Master"
    if rank == 37:
        return f"Legend {get_legend_rank(match, driver, selector)}"
    
    #General Logic
    rank_level = (rank-1)//5
    rank_level = rank_dict.get(rank_level, None)
    rank_stars = get_rank_stars(rank)
    return f"{rank_level} {rank_stars}"
    
def check_if_replay_exists(replay_id, conn):
    try:
        query = f"SELECT COUNT(1) FROM MATCHES WHERE replay_id = '{replay_id}'"
        result = pd.read_sql(query, conn)
        if result.iloc[0,0] == 0:
            return False
        else:
            return True
    except Exception as e:
        print(f"Error in UID: {e}")
        return True
    
def get_highest_dt(uid):
    query = f"""SELECT MAX(occurence_dt) FROM Matches m 
    JOIN Match_Contestants mc ON 
    mc.replay_id = m.replay_id
    WHERE mc.user_id = {uid};
    """
    conn = sqlite3.connect(os.getenv("DBNAME"))
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result.iloc[0,0]

def get_latest_dt(id, conn):
    #Returns the highest dt if it exists
    result = pd.read_sql_query(f"SELECT COUNT(*) FROM Finished_Ids WHERE user_id = {id}", conn)
    if result.iloc[0,0] == 0:
        return None
    else:
        result = pd.read_sql_query(f"SELECT latest_match FROM Finished_Ids WHERE user_id = {id}", conn)
        return result.iloc[0,0]
    
def reached_latest_dt(id, dt, conn):
    query = f"UPDATE Finished_Ids SET latest_match='{dt}' WHERE user_id = {id}"
    conn.execute(query)
    conn.commit()