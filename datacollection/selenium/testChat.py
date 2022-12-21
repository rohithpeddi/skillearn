from selenium import webdriver
import time

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome_driver_binary = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"

driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
driver.get('http://codepad.org')

text_area = driver.find_element_by_id('textarea')
text_area.send_keys("This text is send using Python code.")