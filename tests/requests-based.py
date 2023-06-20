import os
import requests
from bs4 import BeautifulSoup

modem_url = os.getenv('MODEM_URL', 'https://192.168.100.1/')
modem_user = os.getenv('MODEM_USER', 'admin')
modem_pass = os.getenv('MODEM_PASS')

def get_metrics():
    # Authenticate with the modem
    session = requests.Session()
    session.auth = (modem_user, modem_pass)
    session.verify = False  # Ignore SSL certificate errors
    
    # Load the metrics page
    metrics_url = modem_url + '/' + 'cmconnectionstatus.html'
    response = session.get(metrics_url)
    
    # Parse the metrics from the HTML response
    soup = BeautifulSoup(response.content, 'html.parser')
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
        print(response.text)

# Call the function to get the metrics
get_metrics()