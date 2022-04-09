from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://replit.com/login")
id_input = driver.find_element(By.XPATH, "//*[@id='__next']/div/div[2]/div/div/div[1]/form/div[2]/div[1]/div/input")
password_input = driver.find_element(By.XPATH, "//*[@id='__next']/div/div[2]/div/div/div[1]/form/div[2]/div[2]/div/div/input")
login_btn = driver.find_element(By.XPATH, "//span[text() = 'Log in']/..")

id_input.send_keys(input("id: "))
password_input.send_keys(input("password: "))
login_btn.click()

input()