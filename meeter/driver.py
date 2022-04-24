import logging, os
from selenium import webdriver
from selenium.webdriver.chrome.service  import Service as ChromeService
from selenium.webdriver.edge.service    import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService

from globalvar import global_vars as gl

def chrome():
    logging.info('Creating browser driver...')
    config = gl['config']['driver']
    # Options
    options = webdriver.ChromeOptions()
    # Service
    driver_path = config['path']
    log_path = os.path.join('logs', 'driver', gl['start_time']+'.log')
    print(log_path)
    service = ChromeService(executable_path=driver_path, log_path=log_path)
    # Driver
    driver = webdriver.Chrome(options=options, service=service)
    driver.get(config['start_page'])
    logging.info('Created successfully')
    return driver