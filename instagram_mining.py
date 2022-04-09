import time
import json
import csv
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

class InstagramMiner:
    def __init__(self, initial_hashtag, max_hashtags, interval=10):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.initial_hashtag = initial_hashtag
        self.max_hashtags = max_hashtags
        self.interval = interval
        self.collected_hashtags = {}

    def wait_for(self, wait, ec, locator):
        return WebDriverWait(self.driver, wait).until(ec(locator))
    
    def prepare(self):
        self.reports = Path("reports")
        self.reports.mkdir(exist_ok=True)
    
    def save_file(self):
        with open(self.reports / f"{self.initial_hashtag}-report.csv", "w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Hashtag", "Post Count"])
            for collected in self.collected_hashtags.items():
                writer.writerow(collected)
        json.dump(self.collected_hashtags, open(self.reports / f"{self.initial_hashtag}-report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    
    def start(self):
        self.prepare()
        print(f"Collecting {self.initial_hashtag}")

        self.driver.get(f"https://www.instagram.com/")
        cookies = json.load(open("instagram_cookie.json", encoding="utf-8"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.get(f"https://www.instagram.com/accounts/login/")
        try:
            ID, PASSWORD = open("instagram_account.txt").read().splitlines()
            id_input, pass_input = self.wait_for(5, EC.presence_of_all_elements_located, (By.CSS_SELECTOR, "input"))
            id_input.send_keys(ID)
            pass_input.send_keys(PASSWORD)
            pass_input.send_keys(Keys.RETURN)
            self.wait_for(5, EC.url_to_be, "https://www.instagram.com/accounts/onetap/?next=%2F")
        except Exception:
            pass

        self.get_related(self.initial_hashtag)
        self.finish()

    def finish(self):
        self.driver.quit()
        self.save_file()

    def extract_data(self):
        hashtag_name = self.wait_for(10, EC.presence_of_element_located, (By.CSS_SELECTOR, "h1"))
        hashtag_name = hashtag_name.text.removeprefix("#")
        post_count = self.driver.find_element(By.XPATH, "//div[contains(text(), '게시물')]/span")
        post_count = int(post_count.text.replace(",", ""))

        if hashtag_name not in self.collected_hashtags:
            self.collected_hashtags[hashtag_name] = post_count
        print(f"Collected {hashtag_name}: {post_count}")
        time.sleep(self.interval)
        return hashtag_name

    def get_related(self, target_hashtag=None):
        if target_hashtag:
            self.driver.get(f"https://www.instagram.com/explore/tags/{target_hashtag}/")
        else:
            self.driver.switch_to.window(self.driver.window_handles[0])

        try:
            self.extract_data()
            popular = self.wait_for(10, EC.presence_of_element_located, (By.XPATH, "//div[contains(text(), '인기 게시물')]/../following-sibling::div"))
            # recent = driver.find_element(By.XPATH, "//h2[contains(text(), '최근 사진')]/following-sibling::div")
            popular_posts = [i.get_attribute("href") for i in popular.find_elements(By.CSS_SELECTOR, "a")]
        except Exception:
            return

        for post in popular_posts:
            # post.send_keys(Keys.CONTROL, Keys.ENTER)
            # driver.execute_script(f"""window.open("{post.get_attribute("href")}", "_blank");""")
            self.driver.get(post)
            time.sleep(self.interval)
            related_hashtags = [i for i in self.driver.find_elements(By.CSS_SELECTOR, "a") if "explore/tags/" in i.get_attribute("href") and i.text.startswith("#")]
            # print(*[(i.get_attribute("href"), i.text) for i in related_hashtags], sep="\n")

            for i in range(min(len(related_hashtags), self.max_hashtags)):
                if related_hashtags[i].text.removeprefix("#") in self.collected_hashtags:
                    continue
                ActionChains(self.driver).key_down(Keys.CONTROL).click(related_hashtags[i]).key_up(Keys.CONTROL).perform()
                time.sleep(self.interval)

            for window in self.driver.window_handles[1:]:
                self.driver.switch_to.window(window)
                try:
                    self.extract_data()
                except Exception:
                    pass
                if len(self.collected_hashtags) >= self.max_hashtags:
                    return

            for window in self.driver.window_handles[:-1]:
                self.driver.switch_to.window(window)
                self.driver.close()

            self.driver.switch_to.window(self.driver.window_handles[0])

        if len(self.collected_hashtags) < self.max_hashtags:
            self.get_related()

if __name__ == "__main__":
    dogMiner = InstagramMiner("dog", 15)
    dogMiner.start()
    catMiner = InstagramMiner("cat", 10)
    catMiner.start()
