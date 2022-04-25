import logging, os
from selenium import webdriver
from selenium.webdriver.chrome.service  import Service as ChromeService

from global_var import global_vars as gl

def chrome():
    logging.info('Creating browser driver...')
    config = gl['config']['driver']
    # Options
    options = webdriver.ChromeOptions()
    for arg in config['options']['arguments']:
        options.add_argument(arg)
    for key, value in config['options']['experimental_option'].items():
        options.add_experimental_option(key, value)
    # Service
    driver_path = config['path']
    log_path = os.path.join('logs', 'driver', gl['start_time']+'.log')
    service = ChromeService(executable_path=driver_path, log_path=log_path)
    # Driver
    driver = webdriver.Chrome(options=options, service=service)
    driver.get(config['start_page'])
    logging.info('Created successfully')
    return driver