
import socket
import uuid
from angel_order_ws import AngelOrderWS, AngelOrderWSV1
import constant
import requests
import http.client
import json
import pyotp
import enum
import websocket
from zerodha_login import ZerodhaConnect, ZerodhaConnectV2
from hashlib import sha256
from zerodha_db import ZerodhaInstruments


class Account(object):

    def __init__(self, CLIENT_ID, PASSWORD, APIKEY, SECRETKEY, TOTP_KEY, BROKER, RISK='LOW'):
        self.client_id = CLIENT_ID
        self.password = PASSWORD
        self.api_key = APIKEY
        self.secret_key = SECRETKEY
        self.totp_key = TOTP_KEY
        self.broker = BROKER
        self.risk_setting = RISK
        self.accountInfo = {"status": 'true', "message": "SUCCESS", "errorcode": "", "data": {"jwtToken": "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VybmFtZSI6IkExMjk1NjgzIiwicm9sZXMiOjAsInVzZXJ0eXBlIjoiVVNFUiIsImlhdCI6MTY3MzE2MTM1NywiZXhwIjoxNzU5NTYxMzU3fQ.L3NYyts9_oO37zCxGTovWbbZYDTlP7Zq2LplnKKqZ17L6eOh18qZocoLuDWf9WkOnZZ5PSAbfeloxR43aNVmmQ",
                                                                                              "refreshToken": "eyJhbGciOiJIUzUxMiJ9.eyJ0b2tlbiI6IlJFRlJFU0gtVE9LRU4iLCJpYXQiOjE2NzMxNjEzNTd9.qciX-XwoTVJgE2KLqGOyC4nV8xuxY_K_3-9_juLQ0RPaiE8ylPdhGXHIw6IoKnqu3ilJ76WdKtWQVq4YFVseJA", "feedToken": "0806422956"}}
        self.tempAccountInfo = {
            "jwtToken": "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VybmFtZSI6IkExMjk1NjgzIiwicm9sZXMiOjAsInVzZXJ0eXBlIjoiVVNFUiIsImlhdCI6MTY3MTMwMzMyMCwiZXhwIjoxNzU3NzAzMzIwfQ.kzm66HD1DdTDKXHzGJ4H4UybGBzKVUETpDsOhQ1_spKxnjiPZK_c1FqyyrHyLjXIlh2b2x8a1fv0ohSEV3Y3Rg",
            "refreshToken": "eyJhbGciOiJIUzUxMiJ9.eyJ0b2tlbiI6IlJFRlJFU0gtVE9LRU4iLCJpYXQiOjE2NzEzMDMzMjB9.dV4lHsgIoi_t48jFsanmN-Ekf77sPTbOJ3rCaIpuFVU0eRwu0gYIDRXxV0ASQS9aMvPp5I6IB6FPr5LeEkyM5w",
            "feedToken": "0887245285"
        }
        self.userProfile = ''
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            # 'X-ClientLocalIP': s.getsockname()[0],
            # 'X-ClientLocalIP': constant.CLIENTLOCALIP,
            # 'X-ClientPublicIP': format(ip),
            # 'X-ClientPublicIP': constant.CLIENTLOCALIP,
            # 'X-MACAddress': constant.MACADDRESS,
            # 'X-PrivateKey': constant.APIKEY
        }
        # 'Logged Out' 'Login Error' 'Logged In'
        self.authStatus = 'Logged Out'
        if self.broker == 'zerodha':
            self.conn = http.client.HTTPSConnection(
                "api.kite.trade")
        else:
            # self.create_headers()
            self.conn = http.client.HTTPSConnection(
                "apiconnect.angelbroking.com")

        """ WS CONSTANTS """
        self.HB_INTERVAL = 30
        self.HB_THREAD_FLAG = False
        self.WS_RECONNECT_FLAG = False
        self.ws = None
        self.task_dict = {}
        # self.loginTest()
        # self.WSOBJECTCONTAINER = AngelOrderWS()
        self.WSOBJECTCONTAINER = AngelOrderWSV1()
        self.WSOBJECTCONTAINER.setDaemon(True)
        # self.WSOBJECTCONTAINER.start()

    def __str__(self):
        return ("Arm object:\n"
                "  CLIENT_ID = {0}\n"
                "  PASSWORD = {1}\n"
                "  APIKEY = {2}\n"
                "  SECRETKEY = {3} \n"
                "  TOTP_KEY = {4} \n"
                "  RISK = {5}"
                .format(self.client_id, self.password, self.api_key, self.secret_key, self.totp_key, self.risk_setting))

    def status(self):
        return (self.client_id, self.password, self.api_key, self.secret_key, self.totp_key, self.authStatus, self.risk_setting)

    def tuple_val(self):
        return tuple((self.client_id, self.password, self.api_key, self.secret_key, self.totp_key, self.broker, self.risk_setting))

    def is_valid(self):
        if self.client_id == None:
            return False
        elif self.password == None:
            return False
        elif self.api_key == None:
            return False
        elif self.secret_key == None:
            return False
        elif self.totp_key == None:
            return False
        else:
            return True

    def create_headers(self):
        retries = 0
        success = False
        while not success and retries < 3:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                print('My ClientLocalIP:{}', s.getsockname()[0])
                ip = requests.get(
                    'https://api.ipify.org').content.decode('utf8')
                print('My public IP address is: {}'.format(ip))
                print("The formatted MAC address is : ", end="")
                mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                        for elements in range(0, 2*6, 2)][::-1])
                print(mac_address)
                self.headers['X-ClientLocalIP'] = s.getsockname()[0]
                self.headers['X-ClientPublicIP'] = format(ip)
                self.headers['X-MACAddress'] = mac_address
                self.headers['X-PrivateKey'] = self.api_key
                s.close()
                success = True
            except Exception as e:
                print(e)
                retries += 1
                self.authStatus = 'Logged Out'

    def wstest(self):
        print('wstest connection')
        websocket.enableTrace(True)
        # wss://demo.piesocket.com/v3/channel_123?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self

        self.ws = websocket.WebSocketApp("wss://demo.piesocket.com/v3/channel_123?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self",
                                         # self.ws = websocket.WebSocketApp(constant.WSORDER,

                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error).run_forever()

        # self.ws.send("Hello, Server")
        # print(self.ws.recv())
        # self.ws.close()
    def login_angel(self):
        retries = 0
        success = False
        while not success and retries < 3:
            try:
                authkey = pyotp.TOTP(self.totp_key)
                payload = {
                    'clientcode': self.client_id,
                    'password': self.password,
                    'totp': authkey.now()
                }
            except Exception as e:
                print(e)
                retries += 1

            # payload = "{\n\"clientcode\":\"CLIENT_ID\",\n\"password\":\"CLIENT_PASSWORD\"\n,\n\"totp\":\"TOTP_CODE\"\n}"

            json_data = json.dumps(payload)
            """ s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            print('My ClientLocalIP:{}',s.getsockname()[0])
            ip = get('https://api.ipify.org').content.decode('utf8')
            print('My public IP address is: {}'.format(ip))
            print ("The formatted MAC address is : ", end="")
            print (':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
            for elements in range(0,2*6,2)][::-1])) 
            
            s.close()"""

            print(payload)
            try:
                self.conn.request("POST", constant.LOGIN,
                                  json_data,
                                  self.headers)

                res = self.conn.getresponse()
                data = res.read()
            except Exception as e:
                print(e)
                retries += 1

            try:
                print(res.status, data.decode("utf-8"))
                if res.status == 200:
                    parsedJson = json.loads(data.decode("utf-8"))
                    if 'errorcode' in parsedJson and parsedJson['errorcode'] != '':
                        self.authStatus = 'Login Error'
                        self.accountInfo = ''
                        retries = 5
                        return
                    else:
                        self.authStatus = 'Logged In'
                        self.accountInfo = parsedJson
                        success = True
                        return
                else:
                    retries = 5
            except ValueError:
                print("Couldn't parse the JSON response received from the server: {content}".format(
                    content=data))
                retries += 1

    def login_zerodha(self):
        # api_key, api_secret, user_id, user_pwd, totp_key
        zerodhaConnectObject = ZerodhaConnectV2(
            self.api_key, self.secret_key, self.client_id, self.password, self.totp_key)
        requestTokenObject = zerodhaConnectObject.fetch_request_token()
        # response['success'] = success
        # response['token'] = ''
        if requestTokenObject['success']:
            self.authStatus = 'Login Error'
            self.accountInfo = ''
            retries = 0
            success = False
            while not success and retries < 3:
                # payload = "{\n\"clientcode\":\"CLIENT_ID\",\n\"password\":\"CLIENT_PASSWORD\"\n,\n\"totp\":\"TOTP_CODE\"\n}"
                h = sha256(self.api_key.encode(
                    "utf-8") + requestTokenObject['token'].encode("utf-8") + self.secret_key.encode("utf-8"))
                checksum = h.hexdigest()

                payload = {
                    "api_key": self.api_key,
                    "request_token": requestTokenObject['token'],
                    "checksum": checksum
                }
                print(payload)
                try:
                    res = requests.post("https://api.kite.trade" + constant.GENERATESESSIONTOKEN,
                                        payload, headers={
                                            "X-Kite-Version": "3"
                                        })
                    print(res)
                    print(res.status_code, res.json(), '195')
                except Exception as e:
                    print(e)
                    retries += 1

                try:
                    print(res.status_code, res.json(), '201')
                    if res.status_code == 200:
                        parsedJson = res.json()
                        if "status" in parsedJson and parsedJson['status'] != 'success':
                            self.authStatus = 'Login Error'
                            self.accountInfo = ''
                            retries = 5
                            return
                        else:
                            self.authStatus = 'Logged In'
                            self.accountInfo = parsedJson
                            success = True
                            return
                    else:
                        retries = 5
                except Exception as e:
                    print("Couldn't parse the JSON response received from the server: {content}".format(
                        content=res), e)
                    retries += 1
        else:
            self.authStatus = 'Login Error'

    def login(self):

        if self.broker == 'zerodha':
            self.login_zerodha()
            pass
        else:
            self.login_angel()
            pass

    def get_user_profile(self):
        if self.broker == 'zerodha':
            self.get_user_profile_zerodha()
        else:
            self.get_user_profile_angel()

    def get_user_profile_angel(self):
        if self.authStatus == 'Logged In':
            try:
                self.headers['Authorization'] = "Bearer {0}".format(
                    self.accountInfo['data']['jwtToken'])
                print(self.headers)
                self.conn.request("GET", constant.USERPROFILE, {},
                                  self.headers)
                res = self.conn.getresponse()
                data = res.read()

            except ValueError:
                print("Error occured")

            try:
                print(res.status, data.decode("utf-8"))
                if res.status == 200:
                    parsedJson = json.loads(data.decode("utf-8"))
                    if 'errorcode' in parsedJson and parsedJson['errorcode'] != '':
                        print(parsedJson['errorcode'])
                    else:
                        self.userProfile = parsedJson
            except ValueError:
                raise print("Couldn't parse the JSON response received from the server: {content}".format(
                    content=data))
        else:
            print('User not logged in ########################################')

    def get_user_profile_zerodha(self):
        if self.authStatus == 'Logged In':
            try:
                auth_header = self.api_key + ":" + \
                    self.accountInfo['data']['access_token']
                self.headers["Authorization"] = "token {}".format(auth_header)
                self.headers["X-Kite-Version"] = "3"
                print(self.headers)
                self.conn.request("GET", constant.USERPROFILE, {},
                                  self.headers)
                res = self.conn.getresponse()
                data = res.read()

            except ValueError:
                print("Error occured")

            try:
                print(res.status, data.decode("utf-8"))
                if res.status == 200:
                    parsedJson = json.loads(data.decode("utf-8"))
                    if 'errorcode' in parsedJson and parsedJson['errorcode'] != '':
                        print(parsedJson['errorcode'])
                    else:
                        self.userProfile = parsedJson
            except ValueError:
                raise print("Couldn't parse the JSON response received from the server: {content}".format(
                    content=data))
        else:
            print('User not logged in ########################################')

    def generateToken(self):
        self.headers['Authorization'] = "Bearer {0}".format(
            self.accountInfo['data']['jwtToken'])
        print(self.accountInfo['data'])
        print(self.headers)
        self.conn.request("POST", constant.GENERATETOKEN, json.dumps({'refreshToken': self.accountInfo['data']['refreshToken']}),
                          self.headers)

        res = self.conn.getresponse()
        data = res.read()
        self.accountInfo = res.status, data.decode("utf-8")
        print(self.accountInfo)

    def convert_order(self, orderObject):
        var_zerodha_db = ZerodhaInstruments()
        var_zerodha_db.get_specific_instruments_data(
            orderObject['tradingsymbol'])
        if len(var_zerodha_db) != 0:
            print(var_zerodha_db)
        variety_converter = {
            'NORMAL': 'regular',
            'AMO': 'amo',
            'STOPLOSS': 'co'
        }
        ordertype_converter = {
            'MARKET': 'MARKET',
            'LIMIT': 'LIMIT',
            'STOPLOSS_LIMIT': "SL",
            'STOPLOSS_MARKET': 'SL-M'
        }
        producttype_converter = {
            'DELIVERY': 'CNC',
            'CARRYFORWARD': 'NRML',
            'MARGIN': 'MIS',
            'INTRADAY': 'MIS',
            'BO': 'MIS'
        }
        duration_converter = {
            'DAY': 'DAY',
            'IOC': 'IOC'
        }
        return {
            'variety': variety_converter[orderObject['variety']],
            'order_type': ordertype_converter[orderObject['ordertype']],
            'product': producttype_converter[orderObject['producttype']],
            'validity': duration_converter[orderObject['duration']],
            'tradingsymbol': orderObject['tradingsymbol'],
            'exchange': orderObject['exchange'],
            'quantity': int(orderObject['quantity']) if (orderObject['quantity'] != '') else 0,
            'transaction_type': orderObject['transactiontype'],
            'price': float(orderObject['price']) if (orderObject['price'] != '') else 0
        }

    def place_order(self, orderObject):
        """
        Zerodha                                    Angel
        variety(regular,amo,co,iceberg,auction) -> variety(NORMAL,STOPLOSS,AMO,ROBO)
        order_type(MARKET,LIMIT,SL,SL-M)        -> ordertype(MARKET,LIMIT,STOPLOSS_LIMIT,STOPLOSS_MARKET)
        product(CNC,NRML,MIS)                   -> producttype(DELIVERY,CARRYFORWARD,MARGIN,INTRADAY,BO)
        validity(DAY,IOC,TTL)                   -> duration(DAY,IOC)
        """
        response = ''
        if self.broker == 'zerodha':
            response = self.place_order_zerodha(orderObject)
        else:
            response = self.place_order_angel(orderObject)
        return response

    def place_order_angel(self, convertedOrderObject):
        if self.authStatus == 'Logged In':
            retries = 0
            success = False
            while not success and retries < 3:
                try:

                    self.headers['Authorization'] = "Bearer {0}".format(
                        self.accountInfo['data']['jwtToken'])
                    json_data = json.dumps(convertedOrderObject)
                    print(self.headers, json_data)
                    self.conn.request("POST", constant.PLACEORDER, json_data,
                                      self.headers)
                    res = self.conn.getresponse()
                    data = res.read()
                    print(res.status, data.decode("utf-8"))
                    success = True
                    return data.decode("utf-8")
                except:
                    print("Error occured")
                    retries += 1
                    return 'Error occured'

    def place_order_zerodha(self, orderObject):
        convertedOrderObject = self.convert_order(orderObject=orderObject)
        print(convertedOrderObject, orderObject)

        if self.authStatus == 'Logged In':
            retries = 0
            success = False
            while not success and retries < 3:
                try:
                    self.headers = {}
                    auth_header = self.api_key + ":" + \
                        self.accountInfo['data']['access_token']
                    self.headers["Authorization"] = "token {}".format(
                        auth_header)
                    self.headers["X-Kite-Version"] = "3"
                    order_variety = convertedOrderObject['variety']
                    del convertedOrderObject['variety']
                    print(self.headers, convertedOrderObject, '392')
                    res = requests.post("https://api.kite.trade" + constant.PLACEORDERZERODHA +
                                        '/{0}'.format(order_variety),
                                        convertedOrderObject, headers=self.headers)
                    print(res)
                    print(res.status_code, res.json(), '396')
                    success = True
                    return res.json()
                except:
                    print("Error occured")
                    retries += 1
                    return 'Error occured'

    def last_traded_price(self,orderObject):
        response = 0
        if self.broker == 'zerodha':
            response = self.ltp_zerodha(orderObject)
        else:
            response = self.ltp_angel(orderObject)
        return response

    def ltp_zerodha(self,orderObject):
        pass

    def ltp_angel(self,orderObject):
        retries = 0
        success = False
        while not success and retries < 3:
            try:

                self.headers['Authorization'] = "Bearer {0}".format(
                    self.accountInfo['data']['jwtToken'])
                json_data = json.dumps({
                    "exchange": "NSE",
                    "tradingsymbol": "SBIN-EQ",
                    "symboltoken": "3045"
                })
                print(self.headers, json_data)
                self.conn.request("POST", constant.GETINSTRUMENTLTP, json_data,
                                  self.headers)
                res = self.conn.getresponse()
                data = res.read()
                print(res.status, data.decode("utf-8"))
                success = True
                return data.decode("utf-8").ltp
            except:
                print("Error occured")
                retries += 1
                return 0

    def logout(self):
        if self.authStatus == 'Logged In' and self.broker == 'zerodha':
            retries = 0
            success = False
            while not success and retries < 3:
                try:
                    print("https://api.kite.trade" + constant.GENERATESESSIONTOKEN +
                          '?api_key={0}&access_token={1}'.format(self.api_key,
                                                                 self.accountInfo['data']['access_token']), '413')

                    res = requests.delete("https://api.kite.trade" + constant.GENERATESESSIONTOKEN +
                                          '?api_key={0}&access_token={1}'.format(self.api_key,
                                                                                 self.accountInfo['data']['access_token']), headers={
                                              "X-Kite-Version": "3"
                                          })
                    print(res.status_code, res.json(), '417')
                    # self.conn.request("POST", constant.PLACEORDERZERODHA, json_data,
                    #                   self.headers)
                    # res = self.conn.getresponse()
                    # data = res.read()
                    # print(res.status, data.decode("utf-8"))
                    if res.status_code.code == 200:
                        self.authStatus = 'Logged Out'
                    success = True
                    return
                except Exception as e:
                    print("Error occured", e)
                    retries += 1
        if self.authStatus == 'Logged In' and self.broker != 'zerodha':
            retries = 0
            success = False
            while not success and retries < 3:
                try:
                    self.headers['Authorization'] = "Bearer {0}".format(
                        self.accountInfo['data']['jwtToken'])
                    json_data = json.dumps({
                        "clientcode": self.client_id
                    })
                    print(self.headers, json_data)
                    self.conn.request("POST", constant.LOGOUT, json_data,
                                      self.headers)
                    res = self.conn.getresponse()
                    data = res.read()
                    print(res.status, data.decode("utf-8"),'535')
                    if res.status == 200:
                        self.authStatus = 'Logged Out'
                    success = True
                    return
                except Exception as e:
                    print("Error occured", e)
                    retries += 1
        # self.WSOBJECTCONTAINER.close()

    def get_auth_status(self):
        return self.authStatus

    """ WS CODE BEGINS HERE """
