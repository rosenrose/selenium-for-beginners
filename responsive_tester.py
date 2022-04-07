import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from math import ceil
from pathlib import Path

class ResponsiveTester:
  def __init__(self, urls):
    self.urls = urls
    self.options = webdriver.ChromeOptions()
    self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
    self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
    self.driver.maximize_window()
    self.widths = [480, 960, 1366, 1920]
  
  def prepare(self):
    self.screenshots = Path("screenshots")
    self.screenshots.mkdir(exist_ok=True)

  def take_screenshot(self, url):
    self.driver.get(url)
    BROWSER_HEIGHT = self.driver.get_window_size()["height"]
    urlName = url.removeprefix("https://").removeprefix("http://").removesuffix("/").replace("/", "_").strip()
    (urlFolder := self.screenshots / urlName).mkdir(exist_ok=True)

    for width in self.widths:
      self.driver.set_window_size(width=width, height=BROWSER_HEIGHT)
      scroll_height = self.driver.execute_script("""return document.body.scrollHeight;""")
      total_sections = ceil(scroll_height / BROWSER_HEIGHT)

      for section in range(total_sections):
        self.driver.execute_script(f"""window.scrollTo(0, {section * BROWSER_HEIGHT});""")
        time.sleep(0.5)
        self.driver.save_screenshot(str(urlFolder / f"{width}_{section + 1}.png"))

  def start(self):
    self.prepare()
    for url in self.urls:
      self.take_screenshot(url);
    self.finish()

  def finish(self):
    self.driver.quit()

if __name__ == "__main__":
  tester = ResponsiveTester(["https://nomadcoders.co", "https://google.com"])
  tester.start()
