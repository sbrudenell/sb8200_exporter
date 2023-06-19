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

def test_authentication():
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
        tables = soup.find_all('table', class_='simpleTable')
        for table in tables:
            header_row = table.find('tr')
            if header_row:
                header_cells = header_row.find_all('th')
                header = [cell.text.strip() for cell in header_cells]
                print()
                print('-------------------')
                print(header[0])
                print('-------------------')
                print()
            
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 3:
                    metric_name = cells[0].text.strip()
                    metric_status = cells[1].text.strip()
                    metric_comment = cells[2].text.strip()
                    print('Metric:', metric_name)
                    print('Status:', metric_status)
                    print('Comment:', metric_comment)
                    print('---')
                elif len(cells) == 8:
                    channel_id = cells[0].text.strip()
                    lock_status = cells[1].text.strip()
                    modulation = cells[2].text.strip()
                    frequency = cells[3].text.strip()
                    power = cells[4].text.strip()
                    snr_mer = cells[5].text.strip()
                    corrected = cells[6].text.strip()
                    uncorrectables = cells[7].text.strip()
                    print('Channel ID:', channel_id)
                    print('Lock Status:', lock_status)
                    print('Modulation:', modulation)
                    print('Frequency:', frequency)
                    print('Power:', power)
                    print('SNR/MER:', snr_mer)
                    print('Corrected:', corrected)
                    print('Uncorrectables:', uncorrectables)
                    print('---')
                elif len(cells) == 7:
                    channel = cells[0].text.strip()
                    channel_id = cells[1].text.strip()
                    lock_status = cells[2].text.strip()
                    channel_type = cells[3].text.strip()
                    frequency = cells[4].text.strip()
                    width = cells[5].text.strip()
                    power = cells[6].text.strip()
                    print('Channel:', channel)
                    print('Channel ID:', channel_id)
                    print('Lock Status:', lock_status)
                    print('Channel Type:', channel_type)
                    print('Frequency:', frequency)
                    print('Width:', width)
                    print('Power:', power)
                    print('---')
        if not tables:
            print('No metrics table found on the page')
    except Exception as e:
        print("Error occurred during authentication:")
        print(str(e))
    finally:
        # Quit the WebDriver
        driver.quit()

# Call

print('Testing authentication...')
print('-------------------------')
time.sleep(5)
test_authentication()