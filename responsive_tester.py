import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from math import ceil
from pathlib import Path

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://nomadcoders.co")
driver.maximize_window()

widths = [480, 960, 1366, 1920]
BROWSER_HEIGHT = driver.get_window_size()["height"]
(screenshots := Path("screenshots")).mkdir(exist_ok=True)
for png in screenshots.glob("size*.png"):
  png.unlink()

for width in widths:
  driver.set_window_size(width=width, height=BROWSER_HEIGHT)
  scroll_height = driver.execute_script("""return document.body.scrollHeight;""")
  total_sections = ceil(scroll_height / BROWSER_HEIGHT)

  for section in range(total_sections):
    driver.execute_script(f"""window.scrollTo(0, {section * BROWSER_HEIGHT});""")
    driver.save_screenshot(str(screenshots / f"size_{width}_{section + 1}.png"))
    time.sleep(1)

driver.quit()