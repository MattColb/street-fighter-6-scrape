from selenium.webdriver.common.by import By

# Step 1: Parse the cookies.txt file
def parse_netscape_cookies(file_path):
    cookies = []
    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("#") or not line.strip():
                continue  # Skip comments and empty lines
            parts = line.strip().split("\t")
            if len(parts) < 7:
                continue  # Skip invalid lines
            cookie = {
                "domain": parts[0],
                "httpOnly": parts[1].upper() == "TRUE",
                "path": parts[2],
                "secure": parts[3].upper() == "TRUE",
                "expiry": int(parts[4]) if parts[4].isdigit() else None,
                "name": parts[5],
                "value": parts[6]
            }
            cookies.append(cookie)
    return cookies

def add_cookies(driver):
    cookies = parse_netscape_cookies("../cookies-streetfighter-com.txt")

    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"ERROR: {e}")

def close_cookies(driver):
    try:
        if len(driver.find_elements(By.ID, "CybotCookiebotDialogBodyContentTitle")) == 0:
            return
        cookie_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyContentTitle")
        if cookie_button.is_displayed():
            driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
    except Exception as e:
        print(f"Cookie modal not handled: {e}")