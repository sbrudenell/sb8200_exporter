import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import prometheus_client
from prometheus_client.core import GaugeMetricFamily, REGISTRY

# Set up environment variables
MODEM_URL = os.getenv('MODEM_URL', 'https://192.168.100.1/')
MODEM_USER = os.getenv('MODEM_USER', 'admin')
MODEM_PASS = os.getenv('MODEM_PASS')
SELENIUM_REMOTE = os.getenv('SELENIUM_REMOTE', 'true')
SELENIUM_DRIVER_URL = os.getenv('SELENIUM_DRIVER_URL', 'http://localhost:4444')
PORT = os.getenv('PORT', '8000')
SELENIUM_WAIT_TIMEOUT = int(os.environ.get('SELENIUM_WAIT_TIMEOUT', '20'))

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up Prometheus metrics
class CustomCollector(object):
    def collect(self):
        # Set up the gauge metrics
        upstream_lock_status = GaugeMetricFamily('upstream_lock_status', 'Lock status of upstream channels', labels=['channel_id'])
        upstream_modulation = GaugeMetricFamily('upstream_modulation', 'Modulation of upstream channels', labels=['channel_id'])
        upstream_frequency = GaugeMetricFamily('upstream_frequency', 'Frequency of upstream channels', labels=['channel_id'])
        upstream_power = GaugeMetricFamily('upstream_power', 'Power of upstream channels', labels=['channel_id'])
        upstream_channel_type = GaugeMetricFamily('upstream_channel_type', 'Channel type of upstream channels', labels=['channel_id'])
        upstream_symbol_rate = GaugeMetricFamily('upstream_symbol_rate', 'Symbol rate of upstream channels', labels=['channel_id'])
        upstream_width = GaugeMetricFamily('upstream_width', 'Width of upstream channels', labels=['channel_id'])
        downstream_lock_status = GaugeMetricFamily('downstream_lock_status', 'Lock status of downstream channels', labels=['channel_id'])
        downstream_modulation = GaugeMetricFamily('downstream_modulation', 'Modulation of downstream channels', labels=['channel_id'])
        downstream_frequency = GaugeMetricFamily('downstream_frequency', 'Frequency of downstream channels', labels=['channel_id'])
        downstream_power = GaugeMetricFamily('downstream_power', 'Power of downstream channels', labels=['channel_id'])
        downstream_snr_mer = GaugeMetricFamily('downstream_snr_mer', 'SNR/MER of downstream channels', labels=['channel_id'])
        downstream_corrected = GaugeMetricFamily('downstream_corrected', 'Corrected of downstream channels', labels=['channel_id'])
        downstream_uncorrectables = GaugeMetricFamily('downstream_uncorrectables', 'Uncorrectables of downstream channels', labels=['channel_id'])

        # Set up the Selenium driver
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--ignore-certificate-errors')  # Add this line to ignore certificate errors

        if SELENIUM_REMOTE == 'true':
            driver = webdriver.Remote(command_executor=SELENIUM_DRIVER_URL, options=options)
        else:
            driver = webdriver.Chrome(options=options)

        try:
            # Navigate to the modem login page
            logging.info("Navigating to modem login page")
            driver.get(MODEM_URL)

            # Wait for the login page to load
            logging.info("Waiting for login page to load")
            wait = WebDriverWait(driver, SELENIUM_WAIT_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'form')))

            # Find the username and password inputs
            logging.info("Finding username and password inputs")
            username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
            password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        

            # Enter the username and password
            logging.info("Entering username and password")
            username_input.send_keys(MODEM_USER)
            password_input.send_keys(MODEM_PASS)

            # Find and click the login button
            logging.info("Finding and clicking login button")
            login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginButton")))
            login_button.click()

            # Wait for the page to load after authentication
            logging.info("Waiting for page to load after authentication")
            WebDriverWait(driver, SELENIUM_WAIT_TIMEOUT).until(EC.url_contains("/cmconnectionstatus.html"))

            # Extract the available metrics
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tables = soup.find_all('table', class_='simpleTable')
            for table in tables:
                title_row = table.find_previous_sibling('h3')
                if title_row:
                    title = title_row.text.strip()
                    if title == 'Upstream Bonded Channels':
                        header_row = table.find('tr')
                        if header_row:
                            header_cells = header_row.find_all('th')
                            header = [cell.text.strip() for cell in header_cells]

                        rows = table.find_all('tr')
                        for row in rows:
                            cells = row.find_all('td')
                            # Extract the data from the row
                            channel_id = cells[0].text.strip()
                            add_metric(upstream_lock_status, [channel_id], cells[1].text.strip())
                            add_metric(upstream_modulation, [channel_id], cells[2].text.strip())
                            add_metric(upstream_frequency, [channel_id], cells[3].text.strip())
                            add_metric(upstream_power, [channel_id], cells[4].text.strip())
                            add_metric(upstream_channel_type, [channel_id], cells[5].text.strip())
                            add_metric(upstream_symbol_rate, [channel_id], cells[6].text.strip())
                            add_metric(upstream_width, [channel_id], cells[7].text.strip())

                    elif title == 'Downstream Bonded Channels':
                        header_row = table.find('tr')
                        if header_row:
                            header_cells = header_row.find_all('th')
                            header = [cell.text.strip() for cell in header_cells]

                        rows = table.find_all('tr')
                        for row in rows:
                            cells = row.find_all('td')
                            # Extract the data from the row
                            channel_id = cells[0].text.strip()
                            add_metric(downstream_lock_status, [channel_id], cells[1].text.strip())
                            add_metric(downstream_modulation, [channel_id], cells[2].text.strip())
                            add_metric(downstream_frequency, [channel_id], cells[3].text.strip())
                            add_metric(downstream_power, [channel_id], cells[4].text.strip())
                            add_metric(downstream_snr_mer, [channel_id], cells[5].text.strip())
                            add_metric(downstream_corrected, [channel_id], cells[6].text.strip())
                            add_metric(downstream_uncorrectables, [channel_id], cells[7].text.strip())

                    else:
                        # Skip to the next table
                        continue

        finally:
            # Quit the Selenium driver
            driver.quit()

        # Yield the metrics
        yield upstream_lock_status
        yield upstream_modulation
        yield upstream_frequency
        yield upstream_power
        yield upstream_channel_type
        yield upstream_symbol_rate
        yield upstream_width
        yield downstream_lock_status
        yield downstream_modulation
        yield downstream_frequency
        yield downstream_power
        yield downstream_snr_mer
        yield downstream_corrected
        yield downstream_uncorrectables

def add_metric(metric, labels, value):
    try:
        float_value = float(value)
    except ValueError:
        float_value = 0.0
    if value.lower() in ['locked', 'enabled']:
        float_value = 1.0
    metric.add_metric(labels, float_value)

# Poll the metrics every 60 seconds
while True:
    start_time = time.time()
    REGISTRY.register(CustomCollector())
    time.sleep(60)
    end_time = time.time()
    logging.info(f"Polling metrics took {end_time - start_time:.2f} seconds")