import asyncio, logging, time
from datetime import datetime
from threading import Thread
import json
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from globalvar import global_vars as gl
from .driver import chrome
from .meet import Meet


class Meeter:
    def __init__(self, identifier, password):
        logging.info('Startting the Meeter...')
        try:
            self._driver = chrome()
        except:
            logging.error('Some error happened', exc_info=True)
            exit(1)
        self._isclose = False
        self.load_meetings()
        self.login(identifier, password)
        self.thread = Thread(target=self.check_meetings)
        self.thread.run()
    
    @property
    def isclose(self):
        return self._isclose
    
    def alert(self, msg: str, timeout: int = 1):
        logging.info(msg)
        msg += f'\\n(This message will automatically close in {timeout} seconds.)'
        self._driver.execute_script(f'alert("{msg}");')
        WebDriverWait(self._driver, 1).until(EC.alert_is_present())
        try:
            WebDriverWait(self._driver, timeout).until_not(EC.alert_is_present())
        except TimeoutException:
            self._driver.switch_to.alert.accept()
    
    def login(self, identifier, password):
        """Login a Google account"""
        logging.info('Logging in the Google account...')
        driver = self._driver
        driver.switch_to.new_window('tab')
        driver.get('https://google.com/')
        time.sleep(0.5)
        driver.find_element('xpath', '//*[@id="gb"]/div/div[2]/a').click()
        for name in ['identifier', 'password']:
            # Wait for page onload
            elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located(('xpath', f'//*[@name="{name}"]')))
            time.sleep(0.5)
            for x in eval(name):
                elem.send_keys(str(x))
                time.sleep(0.05)
            elem.send_keys(Keys.ENTER)
        # Wait until back to home page
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(('xpath', '//*[@id="gb"]')))
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        logging.info('Logged in successfully')
    
    def logout(self):
        """未完成"""
        raise PermissionError("未完成")
    
    def close(self):
        self._driver.quit()
        self._isclose = True
        logging.info('Stopped the Meeter')
    
    def set_meeting(self, meet, **kwargs):
        if not isinstance(meet, Meet):
            meet = Meet(meet, **kwargs)
        self._meetings.append(meet)
        self.save_meetings()
        return meet
    def get_meeting(self, index=None):
        meetings = self._meetings
        if index:
            return meetings[index]
        return meetings

    def load_meetings(self):
        meetings = self._meetings = []
        try:
            with open('data\\meets.json', 'r', encoding='utf-8') as file:
                meets = json.load(file)
        except FileNotFoundError:
            logging.warning('No meeting data')
            return
        for meet in meets:
            meetings.append(Meet(meeter=self, **meet))
        return meetings
    
    def save_meetings(self):
        meets = [meet.to_dict() for meet in self._meetings]
        with open('data\\meets.json', 'w', encoding='utf-8') as file:
            json.dump(meets, file)
    
    def remove_meeting(self, meet):
        self._meetings.remove(meet)
    
    def check_meetings(self):
        logging.info('checking meetings')
        print('checking meetings')
        try:
            now = datetime.now()
            for meet in self._meetings:
                if (not meet._joined) and \
                    (datetime.strptime(meet.start_time, gl['time_format']) < now):
                    meet.join()
                elif datetime.strptime(meet.end_time, gl['time_format']) < now:
                    meet.leave()
                    if meet.repeat:
                        self.save_meetings()
            if not self._isclose:
                time.sleep(30)
                self.check_meetings()
        except KeyboardInterrupt:
            self.close()