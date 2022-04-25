import logging, re, time
from datetime import datetime, timedelta
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .global_var import global_vars as gl

class Meet:
    def __init__(self, meeter, code: str, join_msg: str = '早安安',
            start_time: datetime = None, end_time: datetime = None, repeat: datetime = None):
        """
        The simple instance of Google Meet
        :args:
        meeter
        code: the code of the Google Meet
        join_msg: the message send whenever join a meet.
        start: 
        """
        pattern = r'^((https?://)?meet.google.com/)?(\w{3})-?(\w{4})-?(\w{3})(\?.*)?$'
        assert (regex := re.match(pattern, code)), 'invalid meet code'
        self._meeter = meeter
        self._driver = meeter._driver
        self._code = '-'.join(regex.groups()[2:-1])
        self._url = 'https://meet.google.com/' + self._code
        self.join_msg = join_msg
        self._joined = False
        self._start_time = self._to_datetime(start_time)
        self._end_time = self._to_datetime(end_time)
        self._repeat = timedelta(**repeat)
    
    def __repr__(self) -> str:
        return f'<Meet code={self._code}>'
    
    @property
    def code(self):
        return self._code
    @property
    def url(self):
        return self._url
    
    @property
    def start_time(self):
        return self._start_time.strftime(gl['time_format'])
    @start_time.setter
    def start_time(self, time):
        self._start_time = self._to_datetime(time)
    
    @property
    def end_time(self):
        return self._end_time.strftime(gl['time_format'])
    @end_time.setter
    def end_time(self, time):
        self._end_time = self._to_datetime(time)
    
    @property
    def repeat(self):
        return {
            'days': self._repeat.days,
            'seconds': self._repeat.seconds,
            'microseconds': self._repeat.microseconds
        }
    @repeat.setter
    def repeat(self, time: dict|timedelta):
        if isinstance(time, dict):
            time = timedelta(**time)
        self._repeat = time
    
    def to_dict(self):
        return dict(
            code = self.code,
            join_msg = self.join_msg,
            start_time = self.start_time,
            end_time = self.end_time,
            repeat = self.repeat
        )
    
    def _to_datetime(self, t: int|str|dict|time.struct_time) -> datetime | None:
        if t == None:
            return None
        if isinstance(t, str):
            t = datetime.strptime(t, gl['time_format'])
        elif isinstance(t, int):
            t = datetime.fromtimestamp(t)
        elif isinstance(t, dict):
            t = datetime(**t)
        elif isinstance(t, time.struct_time):
            t = datetime.fromtimestamp(time.mktime(t))
        return t
    def _sleep(self, seconds = 0.2):
        """makes some delay"""
        time.sleep(seconds)
    def _focus(self):
        """switch to meeting page"""
        self._driver.switch_to.window(self._handle)
        self._sleep()
    def _find_element(self, xpath):
        return self._driver.find_element('xpath', xpath)
    
    def join(self):
        """joins the meeting"""
        assert not self._joined, "You have joined the meeting."
        logging.info(f'Joining the meeting {self._code}...')
        self._joined = True
        driver = self._driver
        driver.switch_to.new_window('tab')
        self._handle = driver.current_window_handle
        driver.get(self._url)
        print('tyring to join the meeting...')
        # Joins meeting
        elem = WebDriverWait(driver, 600).until(
            EC.presence_of_element_located(('xpath', '//*[text()="準備好加入了嗎？" or text()="你無法加入這場視訊通話"]')))
        # Meeting cannot be joined
        if elem.get_property('innerText') == '你無法加入這場視訊通話':
            msg = f'You do not have the permission to join this meeting {self._code}.'
            logging.error(msg)
            return
        # Mic and WebCam permission
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(('xpath', '//*[text()="立即加入" or text()="要求加入"]'))
        )
        self._sleep(1)
        elem = self._find_element('//*[text()="立即加入" or text()="要求加入"]/../..')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(elem))
        # Closes Mic and WebCam
        ActionChains(driver).key_down(Keys.CONTROL) \
            .send_keys('d').send_keys('e').key_up(Keys.CONTROL).perform()
        self._sleep()
        while True:
            try:
                self._sleep(2)
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located(('xpath', '//*[text()="攝影機和麥克風已停用"]'))
                )
                self._sleep(0.5)
                driver.find_element('xpath', '//*[text()="關閉"]/..').click()
            except TimeoutException:
                break
            except NoSuchElementException:
                continue
        elem.click()
        # Waits to join, retry in 5 minutes
        i = 0
        while i <= 10:
            try:
                WebDriverWait(driver, 300).until(
                    EC.presence_of_element_located(('xpath', f'//*[text()="{self._code}"]')))
                break
            except TimeoutException as e:
                if i == 10:
                    logging.error('Times up!')
                    raise e
                else:
                    logging.warning(f'Times up! Retring to join the meeting {self._code}')
                i += 1
        print(f'Joined the meeting {self._code}!')
        logging.info(f'Joined the meeting {self._code}!')
        if msg := self.join_msg:
            self.send(msg)
        self._sleep()
    
    def leave(self):
        """leaves the meeting"""
        assert self._joined, "You have to join the meeting before leaving."
        self._joined = False
        driver = self._driver
        self._focus()
        self._find_element('//*[@aria-label="退出通話"]').click()
        try:
            elem = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(('xpath', f'//*[text()="直接退出通話"]/..')))
            elem.click()
        except TimeoutException:
            pass
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(('xpath', f'//*[text()="你已離開這場會議"]')))
        print('left')
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        logging.info(f'left the meeting {self._code}...')
        if (repeat := self._repeat):
            self._start_time += repeat
            self._end_time += repeat
        self._sleep()
    
    def toggle(self, name):
        """opens or closes mic/camera or raise hand"""
        assert self._joined, "You have to join the meeting first."
        assert name in ['mic', 'camera', 'hand'], 'invalid name'
        i = {'mic': 1, 'camera': 2, 'hand': 3}.get(name)
        self._focus()
        self._find_element(f'//*[@class="R5ccN"]/div[{i}]/div/div/span/button').click()
        self._sleep()
    
    def send(self, *messages: str, sep=' '):
        """sends the messages"""
        assert self._joined, "You have to join the meeting first."
        messages = [str(msg) for msg in messages]
        panel = self._find_element(f'//*[@data-panel-id="2"]')
        panel.click()
        tab = WebDriverWait(self._driver, 5).until(
            EC.presence_of_element_located(('xpath', '//*[@data-tab-id="2"]')))
        self._sleep(0.5)
        if 'qdulke' in tab.get_property('classList'):
            # tab is close
            panel.click()
            self._sleep()
        msgbox = self._find_element('//*[@id="bfTqV"]')
        msgbox.clear()
        for msg in messages:
            msgbox.send_keys(msg)
            self._sleep()
            msgbox.send_keys(sep)
            self._sleep()
        msgbox.send_keys(Keys.ENTER)
        messages = '"'+'", "'.join(messages)+'"'
        logging.info(f'Sent some messages to the meeting {self._code}: {messages}')
        self._sleep()