import logging, time
from datetime import datetime
import json
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .global_var import global_vars as gl
from .driver import chrome
from .meet import Meet


class Meeter:
    def __init__(self, identifier, password):
        logging.info('Startting the Meeter...')
        try:
            self._driver = chrome()
        except:
            logging.exception('Some error happened')
            exit(1)
        self._isclose = False
        self.load_meetings()
        print('press Ctrl + C to stop this program.')
        self.login(identifier, password)
        self.check_meetings()
    
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
        try:
            # Wait for page onload
            elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located(('xpath', f'//*[@name="identifier"]')))
            time.sleep(0.5)
            for x in identifier:
                elem.send_keys(str(x))
                time.sleep(0.05)
            elem.send_keys(Keys.ENTER)
            elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located(('xpath', f'//*[@name="password"]')))
            time.sleep(0.5)
            for x in password:
                elem.send_keys(str(x))
                time.sleep(0.05)
            elem.send_keys(Keys.ENTER)
            # Wait until back to home page
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(('xpath', '//*[@id="gb"]')))
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            logging.info('Logged in successfully')
        except TimeoutException:
            try:
                error_msgs = ['請輸入有效的電子郵件地址或電話號碼', '找不到您的 Google 帳戶', '密碼錯誤，請再試一次，或按一下 [忘記密碼] 以重設密碼。', '目前無法登入帳戶']
                texts = 'text()="{}"'.format('" or text()="'.join(error_msgs))
                elem = driver.find_element('xpath', f'//*[{texts}]')
                msg = elem.get_property('innerText')
                if msg == '目前無法登入帳戶':
                    msg = 'Unable to login this account: '+msg+\
                        '\n瞭解詳情: https://support.google.com/accounts/answer/7675428'
                elif msg == '密碼錯誤，請再試一次，或按一下 [忘記密碼] 以重設密碼。':
                    msg = 'Incorrect password: '+msg
                else:
                    msg = 'Incorrect email: '+msg
                    print(msg)
                logging.exception(msg, exc_info=False)
            except:
                logging.exception('Unknown error happened')
            self.close()
        except:
            logging.exception('Unknown error happened')
            self.close()
    
    def logout(self):
        """未完成"""
        driver = self._driver
        driver.switch_to.new_window('tab')
        driver.get('https://accounts.google.com/logout')
        logging.info('logged out.')
    
    def close(self):
        self._driver.quit()
        self._isclose = True
        logging.info('Stopped the Meeter')
        print('Stopped the Meeter')
        exit()
    
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
            json.dump(meets, file, ensure_ascii=False, indent=2)
    
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
                    if not meet.repeat:
                        self.remove_meeting(meet)
                    self.save_meetings()
            if not self._isclose:
                time.sleep(30)
                self.check_meetings()
        except KeyboardInterrupt:
            self.close()