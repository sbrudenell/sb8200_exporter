import os, time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

modem_url = os.getenv('MODEM_URL', 'https://192.168.100.1/')
modem_user = os.getenv('MODEM_USER', 'admin')
modem_pass = os.getenv('MODEM_PASS')

selenium_remote = os.getenv('SELENIUM_REMOTE', 'true')
selenium_driver_url = os.getenv('SELENIUM_DRIVER_URL', 'http://localhost:4444')

# Collect the metrics from the modem - LOGIN REQUIRED via Selenium
def collect_modem_metrics_html(modem_url):
    url = modem_url
    username = modem_user
    password = modem_pass
    
    # Configure the Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode without opening a browser window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    if selenium_remote == 'true':
        print("Using remote Selenium WebDriver at " + selenium_driver_url)
        driver = webdriver.Remote(selenium_driver_url,options=options)
    else:
        print("Using local Selenium WebDriver")
        driver = webdriver.Chrome(options=options)
    
    try:
        # Load the login page
        print("Loading login page")
        driver.get(url)
        
        # Find the username and password input fields
        print("Waiting for login page to load")
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        
        # Enter the username and password
        print("Entering username and password")
        username_input.send_keys(username)
        password_input.send_keys(password)
        
        # Find and click the login button
        print("Waiting for login button to load")
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginButton")))
        print("Clicking login button")
        login_button.click()
        
        # Wait for the page to load after authentication
        print("Waiting for page to load after authentication")
        WebDriverWait(driver, 10).until(EC.url_contains("/cmconnectionstatus.html"))
        
        # Print the request and response
        print("Request:")
        print(driver.current_url)
        
        # Extract and print the available metrics
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        print("Error occurred during authentication:")
        print(str(e))
        return
    finally:
        # Quit the WebDriver
        driver.quit()
        # Return the BeautifulSoup object containing the metrics
        return soup
    

