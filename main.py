from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

KEYWORD = "buy domain"
(screenshots := Path("screenshots")).mkdir(exist_ok=True)
for png in screenshots.iterdir():
  png.unlink()

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://google.com")

search_bar = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
search_bar.send_keys(KEYWORD)
search_bar.send_keys(Keys.RETURN)

related_questions = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '관련 질문')]/../../../../..")))
driver.execute_script("""
  console.log(arguments)
  arguments[0].remove();
""", related_questions)

search_results = driver.find_elements(By.CSS_SELECTOR, "#search h1 + div > *")
for i, result in enumerate(search_results):
  # title = result.find_element(By.CSS_SELECTOR, "h3")
  # if title:
  #   print(title.text)
  try:
    result.screenshot(f"screenshots/{KEYWORD}_{i + 1:02}.png")
  except:
    pass

input()
driver.quit()