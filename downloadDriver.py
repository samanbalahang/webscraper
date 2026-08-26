from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import os

driver_path = os.path.join(os.path.dirname(__file__), "geckodriver.exe")

service = Service(driver_path)
driver = webdriver.Firefox(service=service)