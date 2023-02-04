import threading
# from kiteconnect import KiteConnect
# from kiteconnect import KiteTicker
# import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time, pyotp
import logging

# logging.basicConfig(level=logging.DEBUG,
#                     format='(%(threadName)-9s) %(message)s',)

api_key = 'lef83s9j4x3xp940'
api_secret = 'mamiwvwlx493z8jnm09jb9zk0adnfkjx'



class ZerodhaConnect(threading.Thread):
    def __init__(self,api_key, api_secret, user_id, user_pwd, totp_key):
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.totp_key = totp_key
        threading.Thread.__init__(self)
    def run(self):
        logging.debug('running')
        # driver = uc.Chrome()
        retries = 0
        success = False
        while not success and retries < 3:
            options = Options()
            options.add_argument("start-maximized")
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            print(retries)
            
            driver = webdriver.Chrome(options=options)

            driver.get(f'https://kite.trade/connect/login?api_key={self.api_key}&v=3')
            login_id = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="userid"]'))))
            
            # login_id = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="userid"]'))
            login_id.send_keys(self.user_id)

            pwd = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="password"]'))))
            # pwd = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="password"]'))
            pwd.send_keys(self.user_pwd)
            time.sleep(3)
            submit = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="container"]/div/div/div[2]/form/div[4]/button'))))

            # submit = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[4]/button'))
            submit.click()

            time.sleep(3)
            #adjustment to code to include totp
            totp = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME,('input'))))
            try:
                # totp = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="totp"]'))
                authkey = pyotp.TOTP(self.totp_key)
                totp.send_keys(authkey.now())
                #adjustment complete
                authorize_btn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="container"]/div/div/form/div/button'))))
                authorize_btn.click()
            except:
                retries+=1
                print('Authorisation for copy-trader not performed')

            try:
                continue_btn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="container"]/div/div/div[2]/form/div[3]/button'))))
                # continue_btn = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[3]/button'))
                continue_btn.click()
            except:
                retries+=1
                print('Authorisation not performed')

            
            request_token = ''
            time.sleep(3)
            try:
                url = driver.current_url
                initial_token = url.split('request_token=')[1]
                request_token = initial_token.split('&')[0]
                print(initial_token,'initial_token >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                driver.close()
                """ kite = KiteConnect(api_key = self.api_key)
                print(request_token)
                data = kite.generate_session(request_token, api_secret=self.api_secret)
                kite.set_access_token(data['access_token']) """
                success = True
                response = {}
                response['success'] = success
                response['token'] = request_token
                return response
            except:
                retries+=1
                print('Token failure')
        response = {}
        response['success'] = success
        response['token'] = ''

        return response

class ZerodhaConnectV2():
    def __init__(self,api_key, api_secret, user_id, user_pwd, totp_key):
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.totp_key = totp_key
        self.response = {}
    # def run(self):
        logging.debug('running')
        # driver = uc.Chrome()
        retries = 0
        success = False
        while not success and retries < 3:
            options = Options()
            options.add_argument("start-maximized")
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            print(retries)
            
            driver = webdriver.Chrome(options=options)

            driver.get(f'https://kite.trade/connect/login?api_key={self.api_key}&v=3')
            login_id = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="userid"]'))))
            
            # login_id = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="userid"]'))
            login_id.send_keys(self.user_id)

            pwd = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="password"]'))))
            # pwd = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="password"]'))
            pwd.send_keys(self.user_pwd)
            time.sleep(3)
            submit = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="container"]/div/div/div[2]/form/div[4]/button'))))

            # submit = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[4]/button'))
            submit.click()

            time.sleep(3)
            #adjustment to code to include totp
            totp = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME,('input'))))
            try:
                # totp = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="totp"]'))
                authkey = pyotp.TOTP(self.totp_key)
                totp.send_keys(authkey.now())
                #adjustment complete
                authorize_btn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="container"]/div/div/form/div/button'))))
                authorize_btn.click()
            except:
                retries+=1
                print('Authorisation for copy-trader not performed')

            try:
                continue_btn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,('//*[@id="container"]/div/div/div[2]/form/div[3]/button'))))
                # continue_btn = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[3]/button'))
                continue_btn.click()
            except:
                retries+=1
                print('Authorisation not performed')

            
            request_token = ''
            time.sleep(3)
            try:
                url = driver.current_url
                initial_token = url.split('request_token=')[1]
                request_token = initial_token.split('&')[0]
                print(initial_token,'request_token >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',request_token)
                """ kite = KiteConnect(api_key = self.api_key)
                print(request_token)
                data = kite.generate_session(request_token, api_secret=self.api_secret)
                kite.set_access_token(data['access_token']) """
                success = True
                
                self.response['success'] = success
                self.response['token'] = request_token
                driver.close()
            except:
                retries+=1
                print('Token failure')
    def fetch_request_token(self):
        return self.response