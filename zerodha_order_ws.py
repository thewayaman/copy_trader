import logging
import threading
import websocket
import base64
import datetime
import ssl
import threading
import time
import zlib
import six
import constant
import json


# logging.basicConfig(level=logging.DEBUG,
#                     format='(%(threadName)-9s) %(message)s',)

class ZerodhaOrderWS(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.wsI = ''
    def run(self):
        print('wstest connection')
        # websocket.enableTrace(True)
        # wss://demo.piesocket.com/v3/channel_123?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self

        self.wsI = websocket.WebSocketApp("wss://ws.kite.trade?api_key=xxx&access_token=xxxx",
                                         # self.ws = websocket.WebSocketApp(constant.WSORDER,

                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)            
        self.wsI.run_forever()
        # self.ws.send("Hello, Server")
        # print(self.ws.recv())
        # self.ws.close()

    def __on_message(self, message):
        print(message)

    def on_message(self,ws, message):
        # print(message,ws)
        pass

    def on_error(self,ws, error):
        print(error)

    def on_close(self,ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self,ws):
        print("Opened connection >>>>>",ws,'>>>>> ws',self.wsI)

    def close(self):
        self.wsI.close()


class ZerodhaWSV1(threading.Thread):
    def __init__(self,CLIENT_ID, APIKEY,ACCOUNT_INFO,threaded_queue):
        threading.Thread.__init__(self)
        self.wsI = ''
        """ WS CONSTANTS """
        self.HB_INTERVAL = 30
        self.HB_THREAD_FLAG = False
        self.WS_RECONNECT_FLAG = False
        self.ws = None
        self.task_dict = {}
        self.client_id = CLIENT_ID
        self.accountInfo = ACCOUNT_INFO
        self.api_key = APIKEY
        self.threaded_queue = threaded_queue
    def run(self):
        print('wstest connection')
        self.HB_THREAD_FLAG = False
        self.initiate_socket_connection()
        while True:
            # More statements comes here
            if self.HB_THREAD_FLAG:
                break
            print(datetime.datetime.now().__str__() +
                  ' : Start task in the background')

            self.heartBeat()

            time.sleep(self.HB_INTERVAL)
        # websocket.enableTrace(True)
    def initiate_socket_connection(self):

        if self.client_id == None or self.accountInfo['data']['access_token'] == None:
            return "client_code or jwtToken or task is missing"
        
        
        print(constant.ZERODHAWSORDER + '?api_key={0}&access_token={1}"'.format(self.api_key, self.accountInfo['data']['access_token']
                                         ))
        headers = {}
        auth_header = self.api_key + ":" + \
            self.accountInfo['data']['access_token']
        headers["Authorization"] = "token {}".format(
            auth_header)
        headers["X-Kite-Version"] = "3"
        self.ws = websocket.WebSocketApp(constant.ZERODHAWSORDER+'?api_key={0}&access_token={1}'
                                         .format(self.api_key, self.accountInfo['data']['access_token']),
                                         header=headers,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error)
        self.ws.run_forever(
            # sslopt={"cert_reqs": ssl.CERT_NONE}
            )

    def terminate_socket_connection(self):
        try:
            self.ws.close()
        except:
            print('An error occured while terminating the connection')

    def __on_message(self, ws, message):
        print(type(message) != bytes)
        # message = '{"type":"order","id":"","data":{"account_id":"ZL3443","unfilled_quantity":0,"checksum":"","placed_by":"ZL3443","order_id":"230324200948857","exchange_order_id":"2100000024359273","parent_order_id":null,"status":"COMPLETE","status_message":null,"status_message_raw":null,"order_timestamp":"2023-03-24 15:24:36","exchange_update_timestamp":"2023-03-24 15:24:36","exchange_timestamp":"2023-03-24 10:43:29","variety":"regular","exchange":"NFO","tradingsymbol":"TCS23APR3360CE","instrument_token":38196482,"order_type":"LIMIT","transaction_type":"BUY","validity":"DAY","product":"NRML","quantity":175,"disclosed_quantity":0,"price":6.25,"trigger_price":0,"average_price":0,"filled_quantity":0,"pending_quantity":175,"cancelled_quantity":175,"market_protection":0,"meta":{},"tag":null,"guid":"66270XLptJ40MwQGlH"}}'
        if type(message) != bytes and type(message) is str:
            message = json.loads(message)
            if message != None and message.get('type')  and message['type'] == 'order':
                self.threaded_queue.put(message)    
        # message = json.loads(message.decode('utf-8'))
        # print('__on_message##################',message,120,message != None and type(message) is dict and message['type'] == 'order')
        # if message != None and message.get('type')  and message['type'] == 'order':
        #     self.threaded_queue.put(message)
        # self._parse_text_message(message)

    def _parse_text_message(self, message):
        print("""Parse text message.""")

        # data = base64.b64decode(message)

        # try:
        #     data = bytes((zlib.decompress(data)).decode("utf-8"), 'utf-8')
        #     data = json.loads(data.decode('utf8').replace("'", '"'))
        #     data = json.loads(json.dumps(data, indent=4, sort_keys=True))
        #     print(data, '_parse_text_message')
        # except ValueError:
        #     return

        # # return data
        # if data:
        #     self._on_message(self.ws, data)

    def _on_message(self, ws, message):
        pass

    def __on_open(self, ws):
        print("__on_open################")
        self.HB_THREAD_FLAG = False
        self._subscribe_on_open()
        if self.WS_RECONNECT_FLAG:
            self.WS_RECONNECT_FLAG = False
            self.resubscribe()
        else:
            self._on_open(ws)

    def _subscribe_on_open(self):
        # request = {"task": "cn", "channel": "NONLM", "token": self.feed_token, "user": self.client_code,
        #            "acctid": self.client_code}
       
        
        self.ws.send(
            json.dumps({
                "type": "order",
                "data": {}
            })
            # json.dumps(request)
        )
        self.WS_RECONNECT_FLAG = False

    def heartBeat(self):
        try:
            # request = {"task": "hb", "channel": "", "token": self.feed_token, "user": self.client_code,
            #            "acctid": self.client_code}
            self.ws.send(
            json.dumps({
                "type": "order",
                "data": {}
            })
            # json.dumps(request)
            )
            self.WS_RECONNECT_FLAG = False

        except:
            print("HeartBeat Sending Failed")
            # time.sleep(60)

    def resubscribe(self):

        self.ws.send(
            json.dumps({
                "type": "order",
                "data": {}
            })
            # json.dumps(request)
        )
        self.WS_RECONNECT_FLAG = False

    def __on_error(self, ws, error):
        print('__on_error#################',error)
        if ("timed" in str(error)) or ("Connection is already closed" in str(error)) or ("Connection to remote host was lost" in str(error)):

            self.WS_RECONNECT_FLAG = True
            self.HB_THREAD_FLAG = True

            if (ws is not None):
                ws.close()
                ws.on_message = None
                ws.on_open = None
                ws.close = None
                # print (' deleting ws')
                del ws

            self.initiate_socket_connection()
        else:
            print('Error info: %s' % (error))
            self._on_error(ws, error)

    def __on_close(self, ws, pos1, pos2):
        self.HB_THREAD_FLAG = True
        print("__on_close################", pos1, pos2)
        self._on_close(ws)

    def _on_open(self, ws):
        pass

    def _on_close(self, ws):
        pass

    def _on_error(self, ws, error):
        pass
