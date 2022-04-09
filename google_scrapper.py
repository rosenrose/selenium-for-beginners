from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

class GoogleKeywordScreenshooter:
    def __init__(self, keyword, screenshots_dir, max_pages):
        self.keyword = keyword
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.screenshots_dir = Path(screenshots_dir)
        self.max_pages = max_pages
    
    def prepare(self):
        self.screenshots_dir.mkdir(exist_ok=True)
        for png in self.screenshots_dir.glob(f"{self.keyword}*.png"):
            png.unlink()

    def start(self):
        self.prepare()
        self.driver.get("https://google.com")
        search_bar = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
        search_bar.send_keys(self.keyword)
        search_bar.send_keys(Keys.RETURN)
        current_page = 1

        while current_page <= self.max_pages:
            try:
                related_questions = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '관련 질문')]/../../../../..")))
                self.driver.execute_script("""
                    console.log(arguments)
                    arguments[0].remove();
                """, related_questions)
            except Exception:
                pass

            search_results = self.driver.find_elements(By.CSS_SELECTOR, "#search h1 + div > *")
            # print(search_results)
            for i, result in enumerate(search_results):
                # title = result.find_element(By.CSS_SELECTOR, "h3")
                # if title:
                #     print(title.text)
                try:
                    result.screenshot(str(self.screenshots_dir / f"{self.keyword}_page{current_page}_{i + 1:02}.png"))
                except Exception:
                    pass
            
            pagination = self.driver.find_element(By.CSS_SELECTOR, "div[role='navigation'] table")
            pages = pagination.find_elements(By.CSS_SELECTOR, "tr td")
            pages[-1].find_element(By.CSS_SELECTOR, "a").click()
            current_page += 1

        self.finish()

    def finish(self):
        self.driver.quit()

if __name__ == "__main__":
    domain_competitors = GoogleKeywordScreenshooter("buy domain", "screenshots", 2)
    python_competitors = GoogleKeywordScreenshooter("python book", "screenshots", 3)
    domain_competitors.start()
    python_competitors.start()
