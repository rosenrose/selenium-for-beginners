import time
import json
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def wait_for(wait, ec, locator):
    return WebDriverWait(driver, wait).until(ec(locator))

def extract_data():
    hashtag_name = wait_for(10, EC.presence_of_element_located, (By.CSS_SELECTOR, "h1"))
    hashtag_name = hashtag_name.text.removeprefix("#")
    post_count = driver.find_element(By.XPATH, "//div[contains(text(), '게시물')]/span")
    post_count = int(post_count.text.replace(",", ""))

    if hashtag_name not in collected_hashtags:
        collected_hashtags[hashtag_name] = post_count
    print(collected_hashtags)
    time.sleep(10)
    return hashtag_name

def get_related(target_hashtag=None):
    if target_hashtag:
        driver.get(f"https://www.instagram.com/explore/tags/{target_hashtag}/")
    else:
        driver.switch_to.window(driver.window_handles[0])

    try:
        extract_data()
        popular = wait_for(10, EC.presence_of_element_located, (By.XPATH, "//div[contains(text(), '인기 게시물')]/../following-sibling::div"))
        # recent = driver.find_element(By.XPATH, "//h2[contains(text(), '최근 사진')]/following-sibling::div")
        popular_posts = [i.get_attribute("href") for i in popular.find_elements(By.CSS_SELECTOR, "a")]
    except Exception:
        return

    for post in popular_posts:
        # post.send_keys(Keys.CONTROL, Keys.ENTER)
        # driver.execute_script(f"""window.open("{post.get_attribute("href")}", "_blank");""")
        driver.get(post)
        time.sleep(10)
        related_hashtags = [i for i in driver.find_elements(By.CSS_SELECTOR, "a") if "explore/tags/" in i.get_attribute("href") and i.text.startswith("#")]
        # print(*[(i.get_attribute("href"), i.text) for i in related_hashtags], sep="\n")

        for hashtag in related_hashtags:
            ActionChains(driver).key_down(Keys.CONTROL).click(hashtag).key_up(Keys.CONTROL).perform()
            time.sleep(10)

        for window in driver.window_handles[1:]:
            driver.switch_to.window(window)
            try:
                extract_data()
            except Exception:
                pass
            if len(collected_hashtags) >= max_hashtags:
                return

        for window in driver.window_handles[:-1]:
            driver.switch_to.window(window)
            driver.close()

        driver.switch_to.window(driver.window_handles[0])

    if len(collected_hashtags) < max_hashtags:
        # get_related(driver.current_url.removesuffix("/").split("/")[-1])
        get_related()

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
cookies = json.load(open("instagram_cookie.json", encoding="utf-8"))

ID, PASSWORD = open("instagram_account.txt").read().splitlines()
driver.get(f"https://www.instagram.com/")
for cookie in cookies:
    driver.add_cookie(cookie)

driver.get(f"https://www.instagram.com/accounts/login/")
try:
    id_input, pass_input = wait_for(5, EC.presence_of_all_elements_located, (By.CSS_SELECTOR, "input"))
    id_input.send_keys(ID)
    pass_input.send_keys(PASSWORD)
    pass_input.send_keys(Keys.RETURN)
    wait_for(5, EC.url_to_be, "https://www.instagram.com/accounts/onetap/?next=%2F")
except Exception:
    pass

initial_hashtag = "dog"
max_hashtags = 20
collected_hashtags = {}

get_related(initial_hashtag)
print(collected_hashtags)

# input()
driver.quit()
