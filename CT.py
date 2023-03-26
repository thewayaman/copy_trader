from tkinter import ttk
from tkinter import tix
from requests import get
import http.client
import json
import mimetypes
from tkinter import *
from glob import glob
from tkinter.messagebox import askyesno, showerror, showwarning, showinfo
from tkinter.filedialog import askopenfilename
import random
import socket
import struct
import uuid
import constant
from openpyxl import load_workbook
from account import Account
from account_db import Account_DB
from angel_db import AngelInstruments
from orders_db import Orders
from zerodha_db import ZerodhaInstruments
from risk_profile_db import RiskProfile
from datetime import datetime
from progress_bar import ProgressBarPanel
import csv
import queue
import copy

# from utility_treads import InternetUtility

Width, Height = 650, 460
imageTypes = [('Gif files', '.gif'),  # for file open dialog
              ('Ppm files', '.ppm'),  # plus jpg with a Tk patch,
              ('Pgm files', '.pgm'),  # plus bitmaps with BitmapImage
              ('All files', '*')]
sheetTypes = [('XLSX files', '.xlsx')]
jsonTypes = [('Json files', '.json')]

APIKEY = '1B55TGBb'
SECRETKEY = 'fee2a674-419e-46a2-9afc-25ee054ea54f'
CLIENT_ID = 'A1295683'
PASSWORD = 'Platinum@10'
CLIENTLOCALIP = '192.168.1.17'
CLIENTPUBLICIP = '122.172.83.83'
MACADDRESS = '16:58:63:8c:33:ce'


class CopyTraderGUI(Frame):
    def __init__(self, parent=NONE, msecs=3000, **args):
        Frame.__init__(self, parent, args)
        self.parent = parent
        self.parent.attributes('-fullscreen', True)
        self.screen_height = parent.winfo_screenheight() - 20
        self.screen_width = parent.winfo_screenwidth() - 200
        self.parent.attributes('-fullscreen', False)
        self.parent.protocol("WM_DELETE_WINDOW", lambda: (self.onQuit()))
        self.style = ttk.Style(self.parent)
        self.style.theme_use(self.style.theme_names()[0])
        self.selectedInstrumentData = ''
        self.instruments = []
        self.listOfAccounts = []
        self.listOfXLSXAccounts = []
        self.threaded_queue = queue.Queue()
        self.Orderframe = None
        # self.parent.after(200, self.listen_for_result)
        # self.parent.after(400, self.simulate_result)
        self.account_risk_vars = ['Low', 'Medium', 'High']
        self.is_place_order_panel_initial_load = True
        self.is_view_order_win_initial_load = True
        self.is_order_modification_win_initial_load = True
        self.is_singleorder_exit_win_initial_load = True
        self.start_progress_bar()
        # if self.check_internet_basic():
        if True:
            self.load_accounts_from_db()
            self.makeWidgets()
            self.createListOfAccountsWidget()
            self.setup_database()
            self.setup_default_risk_profiles()
            self.place_order()
            self.pack(expand=YES, fill=BOTH)
        else:
            try:
                if showerror('Copy Trader', 'Please check if your device is connected to the internet and restart the application') == 'ok':
                    print('west')
                    self.pack(expand=YES, fill=BOTH)
                    self.update()
                    self.quit()
                    self.parent.destroy()
            except Exception as e:
                print(e)
        self.stop_progress_bar()
        self.queue = queue
        self.msecs = msecs
        self.beep = 1
        self.drawn = None

    def check_internet_basic(self, host="8.8.8.8", port=53, timeout=3):
        """ Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP) """

        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
                (host, port))
            return True
        except socket.error as ex:
            print(ex)
            return False
        except Exception as e:
            print(e)
            return False

    def makeWidgets(self):

        self.canvas = Frame(self, height=self.screen_height,
                            width=self.screen_width/2)
        self.canvas.pack_propagate(0)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES, padx=5)
        self.menu = Menu(self)
        account = Menu(self.menu)
        account.add_command(label='Add Account',
                            command=self.addAccountScreen)
        account.add_command(label='Add Risk Rules',
                            command=self.add_risk_rules)
        self.menu.add_cascade(label='Account', menu=account)
        order = Menu(self.menu)
        # order.add_command(label='Place Order', command=self.place_order)
        # order.add_command(label='View Order', command=self.loadOrderScreen)
        order.add_command(label='View Positions',
                          command=self.loadPositionScreen)
        self.menu.add_cascade(label='Order', menu=order)
        self.menu.add_command(label='Quit', command=self.onQuit)
        self.master.configure(menu=self.menu)

    def fetch(self):
        print('Input => "%s"' + self.clientcode.get())  # get text

    def listen_for_result(self):
        """ Check if there is something in the queue. """

        try:
            # self.res
            task = self.threaded_queue.get(0)
            print(task, 'result generated',self.threaded_queue.qsize())
            is_task_done = False
            if type(task) is dict and task.get('type') and task['type'] == 'order' and task['data']:
                list_of_orders = self.order_db.get_orders()
                if len(list_of_orders) > 0:
                    for item in list_of_orders:
                        account_level_orders = json.loads(item[2])
                        for key in account_level_orders.keys():
                            print(account_level_orders[key]['status'],key)
                            if account_level_orders[key]['status'] == 'success' and task['data']['account_id'] == key and task['data']['order_id'] == account_level_orders[key]['data']['order_id']:
                                print(task['data']['account_id'],key,task['data']['order_id'],account_level_orders[key]['data']['order_id'])

                                self.update_order_status(item[0],key,task['data']['status'])
                                if task['data']['status'] == 'COMPLETE':
                                    self.recreate_open_position_tree_for_account(key)
                                is_task_done = True
            if is_task_done == False:
                self.threaded_queue.put(task)


            if self.Orderframe != None and False:
                list_of_ancestors = self.Orderframe.winfo_children()
                if len(list_of_ancestors) > 0:
                    for item in list_of_ancestors:
                        list_of_parents = item.winfo_children()
                        if len(list_of_parents) > 0:
                            for parent in list_of_parents:
                                list_of_children = parent.winfo_children()
                                if len(list_of_children) > 0:
                                    # for  children in list_of_children:
                                    print(list_of_children[0]['text'])
                    print('@@@@@@@@@@@@@@@@@@@@@@@@')
            self.parent.after(500, self.listen_for_result)
        except queue.Empty:
            print('empty queue')
            self.parent.after(1000, self.listen_for_result)

    def simulate_result(self,mock):
        self.threaded_queue.put(mock)
        # self.parent.after(1000, self.simulate_result)

    def loginTest(self):

        conn = http.client.HTTPSConnection(
            "apiconnect.angelbroking.com")
        # payload = "{\n\"clientcode\":\"CLIENT_ID\",\n\"password\":\"CLIENT_PASSWORD\"\n,\n\"totp\":\"TOTP_CODE\"\n}"
        payload = {
            'clientcode': CLIENT_ID,
            'password': PASSWORD,
            'totp': self.totp.get()
        }
        json_data = json.dumps(payload)
        """ s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        print('My ClientLocalIP:{}',s.getsockname()[0])
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))
        print ("The formatted MAC address is : ", end="")
        print (':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
        for elements in range(0,2*6,2)][::-1])) """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            # 'X-ClientLocalIP': s.getsockname()[0],
            'X-ClientLocalIP': CLIENTLOCALIP,
            # 'X-ClientPublicIP': format(ip),
            'X-ClientPublicIP': CLIENTLOCALIP,
            'X-MACAddress': MACADDRESS,
            'X-PrivateKey': APIKEY
        }
        # s.close()

        conn.request("POST", constant.LOGIN,
                     json_data,
                     headers)

        res = conn.getresponse()
        data = res.read()
        print(res.status, data.decode("utf-8"))

    def onStop(self):
        # self.loop = 0
        self.onoff.config(text='Start', command=self.onStart)

    def onOrderFrameConfigure(self, canvas):
        '''Reset the scroll region to encompass the inner frame'''
        canvas.configure(scrollregion=canvas.bbox("all"))

    def place_order(self):

        self.call_progressbar()
        if self.is_place_order_panel_initial_load == False:
            self.place_order_var.destroy()

        if self.is_place_order_panel_initial_load == True:
            self.is_place_order_panel_initial_load = False
        self.orderObject = ''
        self.variety = StringVar()
        self.variety.set('NORMAL')
        self.transactiontype = StringVar()
        self.transactiontype.set('BUY')
        self.ordertype = StringVar()
        self.ordertype.set('MARKET')
        self.producttype = StringVar()
        self.producttype.set('CARRYFORWARD')
        self.duration = StringVar()
        self.duration.set('DAY')
        self.exchange = StringVar()
        self.exchange.set('NFO')
        self.place_order_var = Frame(self,
                                     height=self.screen_height, width=900,
                                     #  padx=20,
                                     pady=15
                                     )
        # win.pack_propagate(0)
        # win.title('Order')
        self.place_order_var.pack(side=TOP)
        # win.config()
        canvas = Canvas(self.place_order_var, borderwidth=0,
                        background="#e0e0e0", width=210)
        accountSettingsFrame = LabelFrame(
            canvas, text='Selected Accounts', height=300, width=200, padx=2)
        accountSettingsFrame.pack(side=RIGHT, fill=Y)

        sbar = Scrollbar(self.place_order_var,
                         orient="vertical", command=(canvas.yview))
        canvas.configure(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=RIGHT, fill=Y)
        canvas.create_window((1, 1), window=accountSettingsFrame, anchor="nw")
        accountSettingsFrame.bind(
            "<Configure>", lambda event, canvas=canvas: self.onOrderFrameConfigure(canvas))

        account_orderplacement_panel = {}
        account_riskpanel = {}
        account_quantity_panel = {}
        account_risk_setting = {}
        for acc in self.listOfAccounts:
            if acc.get_auth_status() == 'Logged In':
                account_frame = LabelFrame(
                    accountSettingsFrame, text=str(acc.client_id), padx=10)
                account_frame.pack(side=TOP, fill=X)

                account_orderplacement_panel[acc.client_id] = BooleanVar()
                account_riskpanel[acc.client_id] = BooleanVar()
                account_quantity_panel[acc.client_id] = DoubleVar()
                account_risk_setting[acc.client_id] = acc.risk_setting
                account_orderplacement_panel[acc.client_id].set(True)
                account_riskpanel[acc.client_id].set(True)

                local_risk_checkbox = Checkbutton(
                    account_frame, text='Risk', var=(account_riskpanel[acc.client_id]))
                local_risk_checkbox.pack(side=LEFT)
                # local_risk_checkbox.select()
                local_checkbox = Checkbutton(
                    account_frame, text='Active', var=(account_orderplacement_panel[acc.client_id]))
                local_checkbox.pack(side=LEFT)

                local_entry = Entry(
                    account_frame, textvariable=account_quantity_panel[acc.client_id], width=10)
                local_entry.pack(side=LEFT)
                # local_checkbox.select()
                print('>>>>>>>>>>>>>>')
                print(account_orderplacement_panel[acc.client_id],
                      account_orderplacement_panel[acc.client_id].get())
                print(account_riskpanel[acc.client_id],
                      account_riskpanel[acc.client_id].get())
                print('<<<<<<<<<<<<<<')
        Isearch = Frame(self.place_order_var, height=300, width=400, pady=2)
        labI = Label(Isearch, width=15, text='Search Instrument')
        self.searchInstrumentItem = Entry(Isearch, width=40)
        self.searchInstrumentItem.bind(
            '<KeyRelease>', (lambda e: self.searchInstruments()))
        Isearch.pack(side=TOP)
        labI.pack(side=LEFT)
        self.searchInstrumentItem.pack(side=LEFT,
                                       expand=YES)
        instrument = Frame(self.place_order_var, height=300, width=400)
        labI = Label(instrument, width=20, text='Instruments')
        sbar = Scrollbar(instrument)
        self.listBoxOfInstruments = Listbox(instrument,
                                            relief=SUNKEN, selectmode=SINGLE, exportselection=False)
        sbar.config(command=(self.listBoxOfInstruments.yview))
        self.listBoxOfInstruments.config(yscrollcommand=(sbar.set))
        sbar.pack(side=RIGHT, fill=Y)
        labI.pack(side=TOP, expand=None, fill=X)
        self.listBoxOfInstruments.pack(side=LEFT,
                                       expand=YES,
                                       fill=BOTH)
        instrument.pack(side=TOP, fill=X)
        db_instrument_list = self.angel_db.get_instruments_data()
        self.instrumentsData = db_instrument_list
        if len(db_instrument_list) != 0:
            for instrument in db_instrument_list:
                self.listBoxOfInstruments.insert(END, instrument[1])

        self.listBoxOfInstruments.bind(
            '<ButtonRelease-1>', (lambda e: self.selectInstrument(
                account_riskpanel,
                account_quantity_panel,
                account_risk_setting
            )))
        selectedInstrument = Frame(
            self.place_order_var, height=300, width=400, pady=2)
        labP = Label(selectedInstrument, width=20,
                     text='Selected Instrument')
        self.selectedInstrument = Entry(selectedInstrument,
                                        width=40, text='Selected Instrument')
        selectedInstrument.pack(side=TOP)
        labP.pack(side=LEFT)
        self.selectedInstrument.pack(side=LEFT, expand=YES)

        self.order_level_risk_checkbox = BooleanVar()
        self.order_level_risk_checkbox.set(False)
        self.order_level_risk_category = StringVar()
        self.order_level_risk_category.set('low')
        risk_panel = LabelFrame(
            self.place_order_var, height=300, width=400, text='Risk management')
        risk_panel.pack(side=TOP, fill=X)
        Radiobutton(risk_panel, text='High', command=(lambda: self.multiplyLots(
            account_riskpanel,
            account_quantity_panel,
            account_risk_setting
        )), variable=(
            self.order_level_risk_category), value='high').pack(side=LEFT)
        Radiobutton(risk_panel, text='Medium', command=(lambda: self.multiplyLots(
            account_riskpanel,
            account_quantity_panel,
            account_risk_setting
        )), variable=(
            self.order_level_risk_category), value='medium').pack(side=LEFT)
        Radiobutton(risk_panel, text='Low', command=(lambda: self.multiplyLots(
            account_riskpanel,
            account_quantity_panel,
            account_risk_setting
        )), variable=(
            self.order_level_risk_category), value='low').pack(side=LEFT)
        Checkbutton(risk_panel, text='Disable Risk Management',
                    command=(lambda: self.multiplyLots(
                        account_riskpanel,
                        account_quantity_panel,
                        account_risk_setting
                    )), padx=30, variable=(self.order_level_risk_checkbox)).pack(side='left')
        combo_frame1 = Frame(self.place_order_var, pady=4)
        exchange = LabelFrame(combo_frame1, height=300,
                              width=400, text='Exchange')
        exchange.pack(side=LEFT)
        radio1 = Radiobutton(exchange, text='BSE EQ', command=(
            lambda: self.orderType()), variable=(self.exchange), value='BSE')
        radio1.pack(side=LEFT)
        radio2 = Radiobutton(exchange, text='NSE EQ', command=(
            lambda: self.orderType()), variable=(self.exchange), value='NSE')
        radio2.pack(side=LEFT)
        radio3 = Radiobutton(exchange, text='NFO', command=(
            lambda: self.orderType()), variable=(self.exchange), value='NFO')
        radio3.pack(side=LEFT)

        orderType = LabelFrame(
            combo_frame1, height=300, width=100, text='Order type')
        orderType.pack(side=LEFT)
        rad1 = Radiobutton(orderType, text='Market', command=(
            lambda: self.orderType()), variable=(self.ordertype), value='MARKET')
        rad1.pack(side=LEFT)
        rad2 = Radiobutton(orderType, text='Limit', command=(
            lambda: self.orderType()), variable=(self.ordertype), value='LIMIT')
        rad2.pack(side=LEFT)
        rad2 = Radiobutton(orderType, text='SL', command=(
            lambda: self.orderType()), variable=(self.ordertype), value='SL')
        rad2.pack(side=LEFT)

        combo_frame1.pack(side=TOP, fill=X)

        combo_frame2 = Frame(self.place_order_var, pady=5)

        producttype = LabelFrame(combo_frame2,
                                 height=300, width=400, text='Product type')
        producttype.pack(side=LEFT)
        rad1 = Radiobutton(producttype, text='CNC', command=(
            lambda: self.orderType()), variable=(self.producttype), value='DELIVERY')
        rad1.pack(side=LEFT)
        rad2 = Radiobutton(producttype, text='NRML', command=(
            lambda: self.orderType()), variable=(self.producttype), value='CARRYFORWARD')
        rad2.pack(side=LEFT)
        rad3 = Radiobutton(producttype, text='MIS', command=(
            lambda: self.orderType()), variable=(self.producttype), value='INTRADAY')
        rad3.pack(side=LEFT)

        buySellFrame = LabelFrame(
            combo_frame2, height=300, width=100, text='Buy/Sell')
        buySellFrame.pack(side=LEFT)
        radio1 = Radiobutton(buySellFrame, text='Buy', command=(
            lambda: self.orderType()), variable=(self.transactiontype), value='BUY')
        radio1.pack(side=LEFT)
        radio2 = Radiobutton(buySellFrame, text='Sell', command=(
            lambda: self.orderType()), variable=(self.transactiontype), value='SELL')
        radio2.pack(side=LEFT)

        order_variety = LabelFrame(
            combo_frame2, height=300, width=100, text='Type')
        order_variety.pack(side=LEFT)
        radio6 = Radiobutton(order_variety, text='Regular', command=(
            lambda: self.orderType()), variable=(self.variety), value='NORMAL')
        radio6.pack(side=LEFT)
        radio7 = Radiobutton(order_variety, text='Iceberg', command=(
            lambda: self.orderType()), variable=(self.variety), value='ICEBERG')
        radio7.pack(side=LEFT)

        combo_frame2.pack(side=TOP, fill=X)

        iceberg_frame = Frame(self.place_order_var, height=300, pady=5)
        iceberg_frame.pack(side=TOP, fill=X)

        labIL = Label(iceberg_frame, width=15, text='Iceberg Leg')
        self.entIL = Spinbox(iceberg_frame, from_=2, to=10, values=(2, 3, 4, 5, 6, 7, 8, 9, 10),
                             width=5, textvariable=IntVar(value=2), wrap=False, command=(),
                             state='readonly')
        labIL.pack(side=LEFT)
        self.entIL.pack(side=LEFT)

        labIQ = Label(iceberg_frame, width=15, text='Iceberg Quantity')
        self.entIQ = Entry(iceberg_frame, width=5, text='Iceberg Quantity')
        labIQ.pack(side=LEFT)
        self.entIQ.pack(side=LEFT)
        radio6.configure(command=(lambda: self.toggle_iceberg(iceberg_frame, 'disable', account_riskpanel,
                                                              account_quantity_panel,
                                                              account_risk_setting)))
        radio7.configure(command=(lambda: self.toggle_iceberg(iceberg_frame, 'normal', account_riskpanel,
                                                              account_quantity_panel,
                                                              account_risk_setting)))

        quantity = Frame(self.place_order_var, height=300,
                         width=100, padx=5, pady=5)
        labL = Label(quantity, width=10, text='Quantity')
        self.entL = Entry(quantity, width=5, text='Lot size')
        labL.pack(side=LEFT)
        self.entL.pack(side=LEFT)
        self.entL.configure(state='normal')
        self.entL.delete(0, END)
        self.entL.insert(0, int(0))
        self.entL.configure(state='disable')
        labM = Label(quantity, width=7, text='Lot')
        current_value_quant = IntVar(value=1)
        self.entM = Spinbox(quantity, from_=0, to=50, values=(0, 10, 20, 30, 40, 50),
                            width=5, textvariable=current_value_quant, wrap=False,
                            command=(lambda: self.multiplyLots(
                                account_riskpanel,
                                account_quantity_panel,
                                account_risk_setting
                            )))
        self.entM.bind('<KeyRelease>', (lambda e: self.multiplyLots(
            account_riskpanel,
            account_quantity_panel,
            account_risk_setting
        )))
        labM.pack(side=LEFT)
        self.entM.pack(side=LEFT)
        labQ = Label(quantity, width=15, text='Total Quantity')
        self.entQ = Entry(quantity, width=10, text='Total Quantity')
        labQ.pack(side=LEFT)
        self.entQ.pack(side=LEFT)

        quantity.pack(side=TOP, fill=X)

        price_combo1 = Frame(self.place_order_var,
                             height=300, width=100, padx=1, pady=5)
        labP = Label(price_combo1, width=5, text='Price')
        self.entP = Entry(price_combo1, width=10, text='Enter Price')
        labP.pack(side=LEFT)
        self.entP.pack(side=LEFT, padx=4)
        price_combo1.pack(side=TOP, fill=X)
        self.toggle_iceberg(iceberg_frame, 'disable', account_riskpanel,
                            account_quantity_panel,
                            account_risk_setting)
        update_price = Button(price_combo1, text='Update Price', command=(
            lambda: self.update_last_traded_price()))
        # cancelBtn = Button(btnsFrame, text='Cancel', command=())
        update_price.pack(side=LEFT)

        labP = Label(price_combo1, width=10, text='Stop Loss')
        self.entSL = Entry(price_combo1, width=10, text='Enter Stop Loss')
        labP.pack(side=LEFT)
        self.entSL.pack(side=LEFT)
        price_combo1.pack(side=TOP, fill=X)

        btnsFrame = Frame(self.place_order_var, height=300,
                          width=400, padx=5, pady=4)
        confirmBtn = Button(btnsFrame, text='Place Order', command=(
            lambda: self.execute_order(
                account_orderplacement_panel,
                account_quantity_panel,
                account_riskpanel,
                self.place_order_var
            )))
        # cancelBtn = Button(btnsFrame, text='Cancel', command=())
        btnsFrame.pack(side=TOP, fill=X)
        confirmBtn.pack(side=LEFT, pady=4, padx=4)
        # cancelBtn.pack(side=LEFT, pady=4, padx=4)
        self.stop_progressbar()

    def toggle_iceberg(self, iceberg_frame, state, account_riskpanel, account_quantity_panel, account_risk_setting):
        if state == 'normal':
            self.ordertype.set('LIMIT')
            self.entIL.configure(state='readonly')
            self.entM.delete(0, END)
            self.entM.insert(0, int(5))

        else:
            self.entIL.configure(state=state)
            self.entM.delete(0, END)
            self.entM.insert(0, int(0))

        self.ordertype.set('MARKET')
        self.entIQ.configure(state=state)
        self.multiplyLots(account_riskpanel,
                          account_quantity_panel,
                          account_risk_setting)

    def multiplyLots(self, riskpanel, quantity_panel, risk_setting):
        """  account_riskpanel,
            account_quantity_panel,
            account_risk_setting """
        # print(type(self.entM.get()),'391 multiply lot')
        # if isinstance(self.entM.get(),str):
        #     showwarning('Copy Trader','Please provide a valid value for multiples')
        #     return
        if self.entM.get() != '' and self.entL.get() != '':
            print(type(self.entM.get()), type(self.entL.get()))
            self.entQ.delete(0, END)
            self.entQ.insert(0, int(float(self.entM.get()))
                             * int(float(self.entL.get())))
        print(self.entM)
        account_risk_matrix = {
            'low': 0,
            'medium': 0,
            'high': 0
        }
        if self.order_level_risk_checkbox.get() == False:
            order_index = 0
            if self.order_level_risk_category.get() == 'low':
                order_index = 2
            elif self.order_level_risk_category.get() == 'medium':
                order_index = 1

            account_risk_matrix['low'] = self.order_risk_profile_var[order_index][0].get(
            )
            account_risk_matrix['medium'] = self.order_risk_profile_var[order_index][1].get(
            )
            account_risk_matrix['high'] = self.order_risk_profile_var[order_index][2].get(
            )
        else:

            account_risk_matrix['low'] = self.account_risk_profile_var[0].get(
            )
            account_risk_matrix['medium'] = self.account_risk_profile_var[1].get(
            )
            account_risk_matrix['high'] = self.account_risk_profile_var[2].get(
            )
        if quantity_panel.values() != 0:
            for elem in quantity_panel.keys():
                print(risk_setting[elem].lower(), elem, account_risk_matrix)
                if self.variety.get() == 'ICEBERG':
                    quant = round(float(0 if self.entM.get() == '' else self.entM.get())
                                  * account_risk_matrix[risk_setting[elem].lower()] / 100)
                    if quant < 5:
                        quantity_panel[elem].set(5)
                    else:
                        quantity_panel[elem].set(quant)
                else:
                    quantity_panel[elem].set(
                        round(float(0 if self.entM.get() == '' else self.entM.get())
                              * account_risk_matrix[risk_setting[elem].lower()] / 100)
                    )
                # print(
                #     elem,
                #     risk_setting[elem],
                #     self.entM.get(),
                #     account_risk_matrix[risk_setting[elem]],
                #     self.order_level_risk_category.get()
                # )

    def loadPositionScreen(self):
        if self.is_view_order_win_initial_load == False:
            self.view_order_win.destroy()
            # self.view_order_win.update()
        if self.is_view_order_win_initial_load == True:
            self.is_view_order_win_initial_load = False

        self.view_order_win = Toplevel(self, height=self.screen_height - 20, width=self.screen_width - 20, padx=10,
                                       pady=10)
        self.view_order_win.pack_propagate(0)
        self.view_order_win.title('View Orders')
        frame_width = int(
            (self.screen_width)/2)
        self.positionscreen_button_orders = Frame(self.view_order_win,padx=10,pady=10)
        refresh_orders = Button(self.positionscreen_button_orders,text='Refresh Orders',command=())
        refresh_orders.configure(state='disable')
        refresh_orders.pack(side=LEFT,fill=NONE)

        add_positions = Button(self.positionscreen_button_orders,text='Add Positions',command=())
        add_positions.configure(state='disable')
        add_positions.pack(side=RIGHT,fill=NONE)

        exit_positions = Button(self.positionscreen_button_orders,text='Exit Positions',command=())
        exit_positions.configure(state='disable')
        exit_positions.pack(side=RIGHT,fill=NONE)

        refresh_positions = Button(self.positionscreen_button_orders,text='Refresh Positions',command=())
        refresh_positions.configure(state='disable')
        refresh_positions.pack(side=RIGHT,fill=NONE)

        self.positionscreen_button_orders.pack(side=TOP,fill=X)


        self.runningOrdersFrame = Frame(self.view_order_win,
                                        width=frame_width,
                                        borderwidth=1, relief=RIDGE)
        column_width = int(frame_width/4)
        self.runningOrdersTree = ttk.Treeview(self.runningOrdersFrame, column=('TIME', 'INSTRUMENT', 'TYPE', 'QUANTITY'), show='headings',
                                              selectmode='extended')
        self.runningOrdersTree.heading('TIME', text='Timestamp')
        self.runningOrdersTree.heading('INSTRUMENT', text='Instrument')
        self.runningOrdersTree.heading('TYPE', text='Type')
        self.runningOrdersTree.heading('QUANTITY', text='Quantity')

        pos = 1
        col_width = self.runningOrdersTree.winfo_width()

        col = 0
        for acc in self.runningOrdersTree['columns']:
            self.runningOrdersTree.column(
                acc, anchor=CENTER, width=column_width)
            pass

        list_of_orders_tuples = self.order_db.get_orders()
        for item in list_of_orders_tuples:
            loaded_order = json.loads(item[1])
            account_level_orders = json.loads(item[2])
            self.runningOrdersTree.insert('', 'end', text=pos, iid=item[0],
                                          values=(
                                              item[0],
                                              loaded_order['tradingsymbol'], loaded_order['transactiontype'],
                                              loaded_order['quantity']), open=True, tags=('order',))
            # order_level_label_frame = Frame(self.runningOrdersFrame,width=400,borderwidth=3,relief=RIDGE)
            # Label(order_level_label_frame,text=
            # item[0] + ' \t' + loaded_order['tradingsymbol'] + '  \t' + loaded_order['transactiontype'] + '  \t' + loaded_order['quantity']
            # ,pady=10,font=(None, 10),wraplength=int(self.screen_width / 2),anchor='w').pack(side=TOP,fill=X)
            pos += 1
            # print(item[0], 'Checker')
            for key in account_level_orders.keys():
                self.runningOrdersTree.insert(item[0], 'end', iid=item[0] + '#' + key,
                                              values=(
                    key,
                    account_level_orders[key]['exchange_order_status'] if account_level_orders[key].get(
                        'exchange_order_status') else 'UNKOWN',
                    # 'Unknown'
                    'Modify',
                    'Delete'), open=True, tags=('content',))

        treeScroll = ttk.Scrollbar(self.runningOrdersFrame)
        treeScroll.configure(command=(self.runningOrdersTree.yview))
        self.runningOrdersTree.configure(yscrollcommand=(treeScroll.set))
        self.runningOrdersTree.tag_configure('order', background='#ecf2fe', font=(
            None, 11))
        self.runningOrdersTree.tag_configure('content', font=(
            None, 9))
        

        self.runningOrdersTree.bind(
            '<ButtonRelease-1>', lambda event: self.open_positions_tree_click_event(event, 'orders'))
        self.runningOrdersTree.pack(side=LEFT, fill=BOTH, anchor='ne')
        treeScroll.pack(side=LEFT, fill=Y)
        self.runningOrdersFrame.pack(side=LEFT, fill=Y, anchor='ne')

        self.openPositionsFrame = Frame(self.view_order_win, width=int(
            (self.screen_width)/2), borderwidth=3, relief=RIDGE)
            
        self.openPositionsTree = ttk.Treeview(self.view_order_win, column=('ACCOUNT_NO','PRODUCT', 'QUANTITY','INSTRUMENT', 'TYPE'), show='headings',
                                              selectmode='extended')
        self.openPositionsTree.heading('ACCOUNT_NO', text='Account No')
        self.openPositionsTree.heading('PRODUCT', text='Product')
        self.openPositionsTree.heading('QUANTITY', text='Quantity')

        for acc in self.openPositionsTree['columns']:
            self.openPositionsTree.column(
                acc, anchor=CENTER, width=int(frame_width/5))
            pass
        pol = 1
        for account in self.listOfAccounts:
            # if account.authStatus == 'Logged In':
                positions = account.get_positions_zerodha()

                self.openPositionsTree.insert('', 'end', iid=account.client_id, text=pol,
                                            values=(
                                                account.client_id), open=True, tags=('order',))
                if (type(positions) is dict) and positions.get('status') and positions['status'] == 'success':
                    for position in positions['data']['net']:
                        self.openPositionsTree.insert(account.client_id, 'end', iid=position['tradingsymbol'] + '#' + account.client_id,
                                                    tags=('content',),
                                                    values=(
                            position['tradingsymbol'],
                            position['product'],
                            position['quantity'],
                            'Add',
                            'Exit'))
                    
                pol += 1

        treeScroll = ttk.Scrollbar(self.openPositionsFrame)
        treeScroll.configure(command=(self.openPositionsTree.yview))
        self.openPositionsTree.configure(yscrollcommand=(treeScroll.set))
        self.openPositionsTree.tag_configure('order', background='#ecf2fe', font=(
            None, 11))
        self.openPositionsTree.tag_configure('content', font=(
            None, 9))
        self.openPositionsTree.bind(
            '<ButtonRelease-1>', lambda event: self.open_positions_tree_click_event(event, 'positions'))
        self.openPositionsTree.pack(side=LEFT, fill=BOTH, anchor='ne')
        treeScroll.pack(side=RIGHT, fill=Y)

    def recreate_running_orders_tree(self):
        list_of_orders_tuples = self.order_db.get_orders()
        if len(self.runningOrdersTree.get_children()) != 0:
            self.runningOrdersTree.delete(*self.runningOrdersTree.get_children())

        pos = 1
        for item in list_of_orders_tuples:
            loaded_order = json.loads(item[1])
            account_level_orders = json.loads(item[2])
            self.runningOrdersTree.insert('', 'end', text=pos, iid=item[0],
                                          values=(
                                              item[0],
                                              loaded_order['tradingsymbol'], loaded_order['transactiontype'],
                                              loaded_order['quantity']), open=True, tags=('order',))
            pos += 1
            for key in account_level_orders.keys():
                self.runningOrdersTree.insert(item[0], 'end', iid=item[0] + '#' + key,
                                              values=(
                    key,
                    account_level_orders[key]['exchange_order_status'] if account_level_orders[key].get(
                        'exchange_order_status') else 'UNKOWN',
                    # 'Unknown'
                    'Modify',
                    'Delete'), open=True, tags=('content',))


    def open_positions_tree_click_event(self, event, tree_type):
        curItem = ''
        col = ''
        if tree_type == 'positions':
            curItem = self.openPositionsTree.item(
                self.openPositionsTree.focus())
            col = self.openPositionsTree.identify_column(event.x)
            row = self.openPositionsTree.identify_row(event.y)
        else:
            curItem = self.runningOrdersTree.item(
                self.runningOrdersTree.focus())
            col = self.runningOrdersTree.identify_column(event.x)
            row = self.runningOrdersTree.identify_row(event.y)
        print('curItem = ', curItem)
        print('col = ', col.split('#'))
        print('row = ', row.split('#'))
        column_pure_number = int(col.split('#')[1])

        if len(curItem['values']) >= column_pure_number:
            print(curItem['values'][column_pure_number - 1])
            selected_cell = curItem['values'][column_pure_number - 1]
            print(selected_cell,'794 selected')
            row_content = row.split('#')

            if selected_cell == 'Delete':
                if curItem['values'][1] == 'CANCELLED' or curItem['values'][1] == 'COMPLETE' or curItem['values'][1] == 'REJECTED':
                    if showerror('Copy Trader',"Order can't be deleted since its already processed",parent=self.view_order_win) == 'ok':
                        return

                try:
                    exg_order_id = self.find_exchange_order_id(
                        row_content[0], row_content[1])
                    self.delete_order_single(exg_order_id, row_content[1],row_content[0])
                except Exception as e:
                    print(e)
                pass
            elif selected_cell == 'Modify':
                if curItem['values'][1] == 'CANCELLED' or curItem['values'][1] == 'COMPLETE' or curItem['values'][1] == 'REJECTED':
                    if showerror('Copy Trader',"Order can't be modified since its already processed",parent=self.view_order_win) == 'ok':
                        return
                try:
                    exg_order_id = self.find_exchange_order_id(
                        row_content[0], row_content[1])
                    self.modify_order_single(exg_order_id, row_content[1])
                except Exception as e:
                    print(e)
            elif selected_cell == 'Exit' and abs(int(curItem['values'][2])) != 0:
                self.exit_position_single(row_content[1],curItem['values'])
                pass

    def multiply_instrument_lots(self):
        if self.exit_quant.get() != '' and self.exit_lot.get() != '':
            print(type(self.exit_quant.get()), type(self.exit_lot.get()))
            self.exit_total_quant.configure(state='normal')
            self.exit_total_quant.delete(0, END)
            self.exit_total_quant.insert(0, int(float(self.exit_quant.get()))
                             * int(float(self.exit_lot.get())))
            self.exit_total_quant.configure(state='disable')
    def exit_position_single(self,parent_tree_id,trade_values_array):
        print(self.openPositionsTree.get_children(parent_tree_id),'MMMMMMMMMM')
        if self.is_singleorder_exit_win_initial_load == False:
            self.single_order_exit_win.destroy()
            
        if self.is_singleorder_exit_win_initial_load == True:
            self.is_singleorder_exit_win_initial_load = False

        self.single_order_exit_win = Toplevel(self, padx=10, width=250,height=190,
                                               pady=10)
        self.single_order_exit_win.title('Exit ' + trade_values_array[0])

        try:
            instrument_response = []
            instrument_response = self.zerodha_db.get_specific_instruments_data_by_tradingsymbol(
            trade_values_array[0])
            print(instrument_response,'instrument_response')
            if len(instrument_response) == 0:
                print(instrument_response)
                if showerror('Copy Trader','Instrument does not exist') == 'ok':
                    self.single_order_exit_win.destroy()
                    return
        except Exception as e:
            print(e, '495 ltp_zerodha')
            return 0
        
        self.exit_ordertype = StringVar()
        self.exit_ordertype.set('MARKET')
        self.exit_producttype = StringVar()

        self.exit_transactiontype = StringVar()


        if int(trade_values_array[2])  < 0:
            self.exit_transactiontype.set('BUY')
        else:
            self.exit_transactiontype.set('SELL')

        buySellFrame = LabelFrame(
            self.single_order_exit_win, height=300, width=100, text='Buy/Sell')
        buySellFrame.pack(side=TOP,fill=X)
        radio1 = Radiobutton(buySellFrame, text='Buy', command=(
            lambda: self.orderType()), variable=(self.exit_transactiontype), value='BUY')
        radio1.pack(side=LEFT)
        radio1.config(state='disable')
        radio2 = Radiobutton(buySellFrame, text='Sell', command=(
            lambda: self.orderType()), variable=(self.exit_transactiontype), value='SELL')
        radio2.pack(side=LEFT)
        radio2.config(state='disable')




        if trade_values_array[1]  == 'NRML':
            self.exit_producttype.set('CARRYFORWARD')
        elif trade_values_array[1]  == 'MIS':
            self.exit_producttype.set('INTRADAY')
        else:
            self.exit_producttype.set('DELIVERY')


        order_type = LabelFrame(self.single_order_exit_win,text='Product type')
        rad1 = Radiobutton(order_type, text='Market', command=(
            lambda: self.orderType()), variable=(self.exit_ordertype), value='MARKET')
        rad1.pack(side=LEFT,fill=NONE)
        rad2 = Radiobutton(order_type, text='Limit', command=(
            lambda: self.orderType()), variable=(self.exit_ordertype), value='LIMIT')
        rad2.pack(side=LEFT,fill=NONE)
        order_type.pack(side=TOP,fill=X)

        producttype = LabelFrame(self.single_order_exit_win,
                                 height=300, width=400, text='Product type')
        producttype.pack(side=TOP, fill=X)
        rad1 = Radiobutton(producttype, text='CNC', command=(
            lambda: self.orderType()), variable=(self.exit_producttype), value='DELIVERY')
        rad1.pack(side=LEFT)
        rad2 = Radiobutton(producttype, text='NRML', command=(
            lambda: self.orderType()), variable=(self.exit_producttype), value='CARRYFORWARD')
        rad2.pack(side=LEFT)
        rad3 = Radiobutton(producttype, text='MIS', command=(
            lambda: self.orderType()), variable=(self.exit_producttype), value='INTRADAY')
        rad3.pack(side=LEFT)

        price_combo1 = Frame(self.single_order_exit_win,
                             height=300, width=100, padx=1, pady=5)
        labP = Label(price_combo1, width=10, text='Price')

        self.exit_price = Entry(price_combo1, width=10, text='Enter Price')
        self.exit_price.delete(0, END)
        self.exit_price.insert(0, float(self.get_last_traded_price(trade_values_array[0],False)))
        
        labP.pack(side=LEFT)
        self.exit_price.pack(side=LEFT)
        price_combo1.pack(side=TOP, fill=X)
        price_combo2 = Frame(self.single_order_exit_win,
                             height=300, width=100, padx=1, pady=5)
        labQ = Label(price_combo2, width=10, text='Quantity')
        self.exit_quant = Entry(price_combo2, width=10, text='Enter Quantity')
        self.exit_quant.delete(0, END)
        self.exit_quant.insert(0, int(instrument_response[0][8]))
        labQ.pack(side=LEFT)
        self.exit_quant.pack(side=LEFT)

        
        labM = Label(price_combo2, width=7, text='Lot')
        
        self.exit_lot = Spinbox(price_combo2, from_=0, to=50, values=(0, 10, 20, 30, 40, 50),
                            width=5, wrap=False,
                            command=(lambda: self.multiply_instrument_lots()))
        self.exit_lot.delete(0,END)
        self.exit_lot.insert(0,abs(int(trade_values_array[2]))/int(instrument_response[0][8]))
        self.exit_lot.bind('<KeyRelease>', (lambda e: self.multiply_instrument_lots()))
        labM.pack(side=LEFT)
        self.exit_lot.pack(side=LEFT)


        labTQ = Label(price_combo2, width=15, text='Total Quantity')
        self.exit_total_quant = Entry(price_combo2, width=10, text='Enter Total Quantity')
        self.exit_total_quant.delete(0, END)
        self.exit_total_quant.insert(0,int(float(self.exit_lot.get())) * int(float(self.exit_quant.get())))
        self.exit_total_quant.configure(state='disable')
        labTQ.pack(side=LEFT)
        self.exit_total_quant.pack(side=LEFT)
        price_combo2.pack(side=TOP, fill=X)
        Button(self.single_order_exit_win,text='Exit Position', width=15 ,
        command=(lambda:self.execute_exit_position(
            parent_tree_id,
            {
                'tradingsymbol':trade_values_array[0],
                'exchange':instrument_response[0][11],
                'transaction_type':self.exit_transactiontype.get() ,
                'order_type':self.exit_ordertype.get(),
                'quantity':int(float(self.exit_total_quant.get())),
                'product':self.exit_producttype.get(),
                'price':float(self.exit_price.get()),
                'validity':'DAY',
                'variety':'regular'
            }
        ))).pack(side=TOP)



        
    def execute_exit_position(self,account_id,order_object):
        account = ''
        response = ''
        print(order_object)
        post_order_success = {}
        for acc in self.listOfAccounts:
            if acc.client_id == account_id:
                post_order_success[acc.client_id] = acc.exit_position(order_object)
                post_order_success[acc.client_id] = {'status': 'success', 'data': {'order_id': '230324202606793'}}
                if post_order_success[acc.client_id] != None and type(post_order_success[acc.client_id]) is dict and post_order_success[acc.client_id].get('status') and post_order_success[acc.client_id]['status'] == 'success':
                    self.single_order_exit_win.destroy()
        local_order_insertion_copy = copy.deepcopy(order_object)
        local_order_insertion_copy['variety'] = 'regular'
        local_order_insertion_copy['transactiontype'] = local_order_insertion_copy['transaction_type']
        local_order_insertion_date = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        sql_insertion_dump = {}
        for key in post_order_success.keys():
            if post_order_success.get(key) and (type(post_order_success[key]) is dict) and post_order_success[key].get('status') and post_order_success[key]['status'] == 'success':
                sql_insertion_dump[key] = copy.deepcopy(
                    post_order_success[key])
                sql_insertion_dump[key]['exchange_order_status'] = 'OPEN PENDING'
        if len(sql_insertion_dump.keys()) > 0:
            self.order_db.insert_order((
                local_order_insertion_date,
                json.dumps(local_order_insertion_copy),
                json.dumps(sql_insertion_dump)
            ))
            self.loadPositionScreen()
        self.post_order_execeution_screen(post_order_success, 'Order Screen')
        # self.recreate_running_orders_tree()
        # self.simulate_result({"type":"order","id":"","data":{"account_id":"ZL3443","unfilled_quantity":0,"checksum":"","placed_by":"ZL3443","order_id":"230324200948857","exchange_order_id":"2100000024359273","parent_order_id":'null',"status":"REJECTED","status_message":'null',"status_message_raw":'null',"order_timestamp":"2023-03-24 15:24:36","exchange_update_timestamp":"2023-03-24 15:24:36","exchange_timestamp":"2023-03-24 10:43:29","variety":"regular","exchange":"NFO","tradingsymbol":"TCS23APR3360CE","instrument_token":38196482,"order_type":"LIMIT","transaction_type":"BUY","validity":"DAY","product":"NRML","quantity":175,"disclosed_quantity":0,"price":6.25,"trigger_price":0,"average_price":0,"filled_quantity":0,"pending_quantity":175,"cancelled_quantity":175,"market_protection":0,"meta":{},"tag":'null',"guid":"66270XLptJ40MwQGlH"}})

    def recreate_open_position_tree_for_account(self,parent_tree_id):

        if len(self.openPositionsTree.get_children(parent_tree_id)) != 0:
                self.openPositionsTree.delete(*self.openPositionsTree.get_children(parent_tree_id))
        
        account = ''
        for acc in self.listOfAccounts:
            if acc.client_id == parent_tree_id and acc.authStatus == 'Logged In':
                account = acc
        positions = account.get_positions_zerodha_update()
        
        if account != '' and (type(positions) is dict) and positions.get('status') and positions['status'] == 'success':
            for position in positions['data']['net']:
                self.openPositionsTree.insert(account.client_id, 'end', iid=position['tradingsymbol'] + '#' + account.client_id,
                                            tags=('content',),
                                            values=(
                    position['tradingsymbol'],
                    position['product'],
                    position['quantity'],
                    'Add',
                    'Exit'))
    def recreate_open_position_tree(self):
        if len(self.openPositionsTree.get_children()) != 0:
                self.openPositionsTree.delete(*self.openPositionsTree.get_children())
        
        pol = 1
        for account in self.listOfAccounts:
            if account.authStatus == 'Logged In':
                positions = account.get_positions_zerodha()

                self.openPositionsTree.insert('', 'end', iid=account.client_id, text=pol,
                                            values=(
                                                account.client_id), open=True, tags=('order',))
                if (type(positions) is dict) and positions.get('status') and positions['status'] == 'success':
                    for position in positions['data']['net']:
                        self.openPositionsTree.insert(account.client_id, 'end', iid=position['tradingsymbol'] + '#' + account.client_id,
                                                    tags=('content',),
                                                    values=(
                            position['tradingsymbol'],
                            position['product'],
                            position['quantity'],
                            'Add',
                            'Exit'))
                        
                pol += 1

    def find_exchange_order_id(self, order_id, account_id):
        exchange_order_id = ''
        list_of_orders = self.order_db.get_order_by_timestamp(order_id)
        if len(list_of_orders) > 0:
            loaded_order_json = json.loads(
                list_of_orders[0][2])[account_id]
            exchange_order_id = loaded_order_json['data']['order_id']
        return exchange_order_id

    def delete_order_all(self, exchange_order_id):
        if showwarning('Copy Trader', 'Are you sure you want to delete this order?') == 'ok':
            print('execute delete')
            for acc in self.listOfAccounts:
                if acc.authStatus == 'Logged In':
                    try:
                        deletion_response = acc.cancel_order(exchange_order_id)
                        showinfo('Cancel Order', deletion_response,
                                 parent=self.view_order_win)
                    except Exception as e:
                        print(e)
                        showerror(
                            'Copy Trader', 'Something went wrong please try again later')
                else:
                    showinfo(
                        'Copy Trader', 'Please login to delete this order', parent=self.view_order_win)

    def delete_order_single(self, exchange_order_id, account_number,order_id):
        if showwarning('Copy Trader', 'Are you sure you want to delete this order?', parent=self.view_order_win) == 'ok':
            print('execute delete')
            is_account_logged_in = False

            for acc in self.listOfAccounts:
                # print(acc.client_id,account_number,'delete_order_single')
                if acc.client_id == account_number and acc.authStatus == 'Logged In':
                    print('delete_order_single', acc)
                    is_account_logged_in = True
                    try:
                        deletion_response = acc.cancel_order(exchange_order_id)
                        showinfo('Cancel Order', deletion_response,
                                 parent=self.view_order_win)
                        if deletion_response['status'] == 'success':
                            self.update_order_status(order_id,account_number,'CANCELLED')

                    except Exception as e:
                        print(e)
                        showerror(
                            'Copy Trader', 'Something went wrong please try again later', parent=self.view_order_win)

            if is_account_logged_in == False:
                showerror(
                        'Copy Trader',"The account isn't logged in for order deletion", parent=self.view_order_win)

    def update_order_status(self, order_id, account_id,status):
        # exchange_order_id = ''
        list_of_orders = self.order_db.get_order_by_timestamp(order_id)
        if len(list_of_orders) > 0:
            loaded_order_wise_json = json.loads(
                list_of_orders[0][2])
            loaded_order_json = loaded_order_wise_json[account_id]
            loaded_order_json['exchange_order_status'] = status
        self.order_db.update_order_status(json.dumps(loaded_order_wise_json),order_id)
        self.recreate_running_orders_tree()
        # print(loaded_order_wise_json)


    def modify_order_single(self, exchange_order_id, account_number):
        if self.is_order_modification_win_initial_load == False:
            self.order_modification_win.destroy()
            # self.view_order_win.update()
        if self.is_order_modification_win_initial_load == True:
            self.is_order_modification_win_initial_load = False

        self.order_modification_win = Toplevel(self, padx=10,
                                               pady=10)

        self.mod_ordertype = StringVar()
        self.mod_ordertype.set('MARKET')
        order_type = Frame(self.order_modification_win)
        rad1 = Radiobutton(order_type, text='Market', command=(
            lambda: self.orderType()), variable=(self.mod_ordertype), value='MARKET')
        rad1.pack(side=LEFT,fill=NONE)
        rad2 = Radiobutton(order_type, text='Limit', command=(
            lambda: self.orderType()), variable=(self.mod_ordertype), value='LIMIT')
        rad2.pack(side=RIGHT,fill=NONE)
        order_type.pack(side=TOP,fill=X)
        price_combo1 = Frame(self.order_modification_win,
                             height=300, width=100, padx=1, pady=5)
        labP = Label(price_combo1, width=10, text='Price')
        self.modified_price = Entry(price_combo1, width=10, text='Enter Price')
        labP.pack(side=LEFT)
        self.modified_price.pack(side=RIGHT)
        price_combo1.pack(side=TOP, fill=X)
        price_combo2 = Frame(self.order_modification_win,
                             height=300, width=100, padx=1, pady=5)
        labQ = Label(price_combo2, width=10, text='Quantity')
        self.modified_quant = Entry(price_combo2, width=10, text='Enter Quantity')
        labQ.pack(side=LEFT)
        self.modified_quant.pack(side=RIGHT)
        price_combo2.pack(side=TOP, fill=X)
        Button(self.order_modification_win,text='Modify Order', width=20 ,command=(lambda: self.modify_order(self.mod_ordertype.get(),
                                                                               self.modified_price.get(),
                                                                               quantity=self.modified_quant.get(),
                                                                               account_number=account_number,
                                                                               exchange_order_id=exchange_order_id
                                                                               ))).pack(side=TOP, fill=X)

    def modify_order(self, order_type, price, quantity, account_number, exchange_order_id):
        order_object = {}
        
        print(price,quantity,'1149')
        if order_type != None:
            order_object['order_type'] = order_type
        if price != None and price != '' and float(price) != 0:
            order_object['price'] = float(price)
        if quantity != None and quantity != '' and float(quantity) != 0:
            order_object['quantity'] = int(quantity)
        print(order_object,'order object')
        if showwarning('Copy Trader', 'Are you sure you want to modify this order?', parent=self.view_order_win) == 'ok':
            print('execute modify')
            is_account_logged_in = False
            for acc in self.listOfAccounts:
                # print(acc.client_id,account_number,'delete_order_single')
                if acc.client_id == account_number and acc.authStatus == 'Logged In':
                    print('modify_order', acc)
                    is_account_logged_in = True
                    try:
                        mod_response = acc.modify_order(
                            exchange_order_id, order_object, 'regular')
                        showinfo('Modify Order', mod_response,
                                 parent=self.view_order_win)
                    except Exception as e:
                        print(e)
                        showerror(
                            'Copy Trader', 'Something went wrong please try again later', parent=self.view_order_win)
            if is_account_logged_in == False:
                    showerror(
                            'Copy Trader',"The account isn't logged in for order modifcation", parent=self.view_order_win)

    def onViewOrderFrameConfigure(self, canvas):
        '''Reset the scroll region to encompass the inner frame'''
        canvas.configure(scrollregion=canvas.bbox("all"))

    def rerenderOrderFrame(self):
        print('rerenderOrderFrame')
        if self.Orderframe != None:
            self.Orderframe.destroy()
        self.Orderframe = Frame((self.Ordercanvas), width=700)
        self.Orderframe.pack(side=LEFT, fill=BOTH, expand=True)
        for acc in self.listOfAccounts:
            accFrame = LabelFrame((self.Orderframe),
                                  height=300, width=700, text=(acc.client_id), pady=20)
            columns = ('INSTRUMENT', 'QUANTITY', 'PRICE', 'STATUS')
            acctree = ttk.Treeview(accFrame, columns=columns, show='headings')
            acctree.heading('INSTRUMENT', text='Instrument1')
            acctree.heading('QUANTITY', text='Quantity2')
            acctree.heading('PRICE', text='Price3')
            acctree.heading('STATUS', text='Status4')
            col_width = acctree.winfo_width()
            for acc in self.listOfAccounts:
                acctree.insert('', END, values=(acc.get_tree_view()))
            else:
                accFrame.pack(side=TOP, fill=X, expand=True)
                acctree.pack(side=TOP, fill=X, expand=True)

        else:
            self.Ordercanvas.after(3000, self.rerenderOrderFrame)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.Ordercanvas.configure(scrollregion=self.Ordercanvas.bbox("all"))

    def selectInstrument(self, riskpanel, quantity_panel, risk_setting):
        try:
            index = self.listBoxOfInstruments.curselection()  # on list double-click
            label = self.listBoxOfInstruments.get(index)
            instrument = ''
            for itme in [k for k in self.instrumentsData if label == k[1]]:
                print(itme, '405')
                instrument = itme
            # print(self.instrumentsData[index[0]])
            self.selectedInstrument.configure(state="normal")
            self.selectedInstrument.delete(0, END)
            self.selectedInstrument.insert(0, label)
            self.selectedInstrument.configure(state="disable")
            self.entL.configure(state="normal")
            self.entL.delete(0, END)
            self.entL.insert(0, int(instrument[5]))
            self.entL.configure(state="disable")
            self.multiplyLots(riskpanel, quantity_panel, risk_setting)
            self.selectedInstrumentData = instrument
            print("Selected", label,
                  instrument, instrument[5])
            self.update_last_traded_price()

        except:
            self.selectedInstrumentData = ''
            print("An exception occurred")

    def update_last_traded_price(self):
        try:
            index = self.listBoxOfInstruments.curselection()  # on list double-click
            label = self.listBoxOfInstruments.get(index)
            instrument = ''
            for itme in [k for k in self.instrumentsData if label == k[1]]:
                print(itme, '405')
                instrument = itme
            if instrument != '':
                self.entP.delete(0, END)
                self.entP.insert(
                    0, float(self.get_last_traded_price(instrument)))
        except Exception as e:
            print(e, '605')
            showerror('Copy Trader', 'Please select an instrument to fetch LTP')
            self.entP.delete(0, END)
            self.entP.insert(0, float(0))

    def get_last_traded_price(self, instrument,is_symbol_token = True):

        if len(self.listOfAccounts) != 0:
            for acc in self.listOfAccounts:
                if acc.authStatus == 'Logged In':
                    return acc.last_traded_price(instrument,is_symbol_token)
            return 0
        else:
            return 0

    def execute_order(self, accounts_object, quantity_panel, risk_panel, window_pane):

        print(datetime.now())
        for e in accounts_object.values():
            print(e.get(), 'iteration')

        index = self.listBoxOfInstruments.curselection()
        if len(index) == 0:
            showwarning(
                'Copy Trader', 'Please select an instrument to proceed', parent=window_pane)
            return

        # if isinstance(self.entM.get(),str):
        #     showwarning('Copy Trader','Please provide a valid value for multiples',master=window_pane)
        #     return
        print(index, 'cursor selection 527')
        label = self.listBoxOfInstruments.get(index)
        instrument = ''
        for item in [k for k in self.instrumentsData if label == k[1]]:
            print(item, '405')
            instrument = item

        print('Order :\n  variety = {0}\n  transactiontype = {1}\n  ordertype = {2}\n  producttype = {3} \n  duration = {4} \n  exchange = {5} \n  price = {6} \n  quantity = {7} \n  selected Instrument = {8} \n  symboltoken = {9} \n  tradingsymbol = {10} \n'.format(
            self.variety.get(), self.transactiontype.get(), self.ordertype.get(), self.producttype.get(), self.duration.get(), self.exchange.get(), self.entP.get(), self.entM.get(), instrument[2], instrument[1], instrument[0]))
        orderObject = {
            'variety': self.variety.get(),
            'tradingsymbol': instrument[1],
            'symboltoken': instrument[0],
            'transactiontype': self.transactiontype.get(),
            'exchange': self.exchange.get(),
            'ordertype': self.ordertype.get(),
            'producttype': self.producttype.get(),
            'duration': self.duration.get(),
            'price': self.entP.get(),
            'quantity': self.entQ.get(),
            'triggerprice': self.entSL.get(),
            'iceberg_legs': self.entIL.get(),
            'iceberg_quantity': self.entIQ.get(),
        }

        if len(self.listOfAccounts) == 0:
            showinfo('Copy Trader', 'No accounts to execute orders')
            return

        post_order_success = {}
        is_any_account_logged_in = False
        for acc in self.listOfAccounts:
            if accounts_object.get(acc.client_id) != None and accounts_object.get(acc.client_id).get() == True:

                if acc.get_auth_status() == 'Logged In':
                    is_any_account_logged_in = True
                    if risk_panel[acc.client_id].get() == True:
                        order_object_copy = copy.deepcopy(orderObject)
                        order_object_copy['quantity'] = str(
                            int(round(quantity_panel[acc.client_id].get())) *
                            int(self.entL.get())
                        )
                        # print(order_object_copy,'557',quantity_panel[acc.client_id].get(),
                        # int(round(quantity_panel[acc.client_id].get())),int(self.entL.get()),
                        # int(round(quantity_panel[acc.client_id].get())) *
                        # int(self.entL.get())
                        # )
                        post_order_success[acc.client_id] = acc.place_order(
                            order_object_copy)
                    else:
                        # print(orderObject,'561')
                        post_order_success[acc.client_id] = acc.place_order(
                            orderObject)
                else:
                    # post_order_success[acc.client_id] = 'Not logged in to place orders'
                    pass
            else:
                # post_order_success[acc.client_id] = 'Inactive account'
                pass

        if is_any_account_logged_in == False:
            showinfo('Copy Trader', 'No accounts logged in to execute orders')
            return

        local_order_insertion_copy = copy.deepcopy(orderObject)
        local_order_insertion_date = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        # order_id TEXT PRIMARY KEY,
        # order_json TEXT NOT 'null',
        # order_collection TEXT NOT NULL
        sql_insertion_dump = {}
        for key in post_order_success.keys():
            if post_order_success.get(key) and (type(post_order_success[key]) is dict) and post_order_success[key].get('status') and post_order_success[key]['status'] == 'success':
                sql_insertion_dump[key] = copy.deepcopy(
                    post_order_success[key])
                sql_insertion_dump[key]['exchange_order_status'] = 'OPEN PENDING'
        if len(sql_insertion_dump.keys()) > 0:
            self.order_db.insert_order((
                local_order_insertion_date,
                json.dumps(local_order_insertion_copy),
                json.dumps(sql_insertion_dump)
            ))
            self.loadPositionScreen()
        self.post_order_execeution_screen(post_order_success, 'Order Screen')
        self.recreate_running_orders_tree()

    def post_order_execeution_screen(self, accounts_order_object, title_action):
        win = Toplevel(self, height=500, width=700, padx=10,
                       pady=10)
        win.pack_propagate(0)
        print(title_action, '482')
        win.title(title_action)
        post_execution_tree = ttk.Treeview(win, column=('ITEM', 'VALUE'), show='headings',
                                              selectmode='extended',height=460)
        post_execution_tree.heading('ITEM', text='Item')
        post_execution_tree.heading('VALUE', text='Value')
        pol = 1
        for key, value in accounts_order_object.items():
            post_execution_tree.insert('', 'end', text=pol,
                                          values=(
                                              key,value),tags=('order',))
        post_execution_tree.pack(side=TOP,fill=BOTH)

    def searchInstruments(self):
        # print(self.searchInstrumentItem.get())
        # print([k for k in self.instrumentsData if self.searchInstrumentItem.get().lower() in k['symbol'].lower()])
        pos = 0
        self.listBoxOfInstruments.delete(0, END)
        for item in [k for k in self.instrumentsData if self.searchInstrumentItem.get().lower() in k[1].lower()]:
            self.listBoxOfInstruments.insert(
                pos, item[1])  # or insert(END,label)
            pos = pos + 1

    def orderType(self):
        print('CHecked')

    def openPanel(self):
        self.onStop()
        name = askopenfilename(initialdir=self.opens, filetypes=imageTypes)
        if name:
            if self.drawn:
                self.canvas.delete(self.drawn)
            img = PhotoImage(file=name)
            self.canvas.config(height=img.height(), width=img.width())
            self.drawn = self.canvas.create_image(2, 2, image=img, anchor=NW)
            self.image = name, img

    def onQuit(self):
        self.update()
        if askyesno('PyView', 'Really quit now?'):
            for item in self.listOfAccounts:
                if item.is_valid():
                    item.logout()
            self.quit()

    def fetchUserProfile():
        print('')

    def loadAccounts(self):
        name = askopenfilename(initialdir='.', filetypes=sheetTypes)
        # print(name)
        # name = '/home/jayant/Desktop/Accounts.xlsx'
        print(name, '472')
        loaded_accounts_object = {}
        if name:
            try:
                wb = load_workbook(name)
                ws = wb[wb.sheetnames[0]]
                for idx, row in enumerate(ws.rows):
                    if idx != 0:
                        values = []
                        for cell in row:
                            values.append(cell.value)
                        self.listOfXLSXAccounts.append(values)
                        acc = Account(*values)

                        is_duplicate = False
                        for x in self.listOfAccounts:
                            if x.client_id == acc.client_id:
                                is_duplicate = True

                        if is_duplicate == False and acc.is_valid():
                            acc.login()
                            print(acc.authStatus, acc.authStatus == 'Logged in')
                            if acc.authStatus == 'Logged In':
                                if self.account_db.insert_account_single_entry(
                                        acc.tuple_val()):
                                    self.listOfAccounts.append(acc)
                                loaded_accounts_object[acc.client_id] = 'Loaded'
                            else:
                                loaded_accounts_object[acc.client_id] = 'Failed to load, please check the credentials and retry later'
                                pass
                self.post_order_execeution_screen(
                    loaded_accounts_object, 'Accounts')
                self.recreate_tree()
            except Exception as e:
                if askyesno('Copy Trader', 'An error occured in the file, do you want to retry?'):
                    self.loadAccounts()
                else:
                    pass
        else:
            if askyesno('Copy Trader', 'No file selected, do you want to retry?'):
                self.loadAccounts()

    def load_accounts_from_db(self):
        self.account_db = Account_DB()
        temp_accounts = self.account_db.get_accounts_data()
        print(temp_accounts, 'Temp accounts load')
        if len(temp_accounts) != 0:
            for acc_values in temp_accounts:
                acc = Account(*acc_values)
                if acc.is_valid():
                    self.listOfAccounts.append(acc)
                    self.account_db.insert_account_single_entry(
                        acc.tuple_val())

        self.initiate_login()

    def initiate_login(self):
        for item in self.listOfAccounts:
            print(item)
            if item.authStatus != 'Logged In':
                # item.login()
                item.get_user_profile()

    def initiateSocketConnections(self):
        for item in self.listOfAccounts:
            print(item)
            if item.is_valid():
                item.initiate_socket_connection()
            print("Accessing one single value (eg. CLIENT_ID): {0}".format(
                item.client_id))

    def createListOfAccountsWidget(self):
        self.tree = ttk.Treeview(self.canvas, column=('CLIENT_ID', 'STATUS', 'RISK'), show='headings',
                                 height=8,
                                 selectmode='browse',)
        self.tree.heading('CLIENT_ID', text='Client ID')
        self.tree.heading('STATUS', text='Status')
        self.tree.heading('RISK', text='Risk')

        pos = 1
        col_width = self.tree.winfo_width()
        for acc in self.tree['columns']:
            self.tree.column(acc, anchor=CENTER, width=col_width)

        for acc in self.listOfAccounts:
            self.tree.insert('', 'end', text=pos, values=(acc.get_tree_view()))
            pos += 1

        treeScroll = ttk.Scrollbar(self.canvas)
        treeScroll.configure(command=(self.tree.yview))
        self.tree.configure(yscrollcommand=(treeScroll.set))
        self.tree.bind('<Button-3>', self.on_account_click)
        treeScroll.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

    def on_account_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if self.tree.item(item) != '':
            if self.tree.item(item)['values']:
                selectedItem = self.tree.item(item)['values']
                # selected_account = [x for ind, x in enumerate(self.listOfAccounts) ]

                for ind, x in enumerate(self.listOfAccounts):
                    if x.client_id == selectedItem[0]:
                        selected_account = x
                print('you clicked on', selected_account)
                self.open_accounts_panel(selected_account, selectedItem)

    def open_accounts_panel(self, selected_account_object, selected_item_from_tree):
        win = Toplevel(self, padx=20, pady=20, width=300, height=300)
        win.pack_propagate(0)
        win.title('Account Configure')
        win.config()
        Label(win, text='{0}'.format(selected_account_object)).pack(
            side=TOP, fill=X, padx=10, pady=10)
        edit_delete_frame = Frame(win)
        edit_delete_frame.pack(side=TOP, fill=X, anchor=CENTER)
        Button(edit_delete_frame, text='Edit account',
               command=(lambda: ())).pack(side=LEFT)
        Button(edit_delete_frame, text='Delete account',
               command=(lambda: self.remove_account(
                   selected_account=selected_account_object, account_screen=win))
               ).pack(side=RIGHT)
        login_logout_frame = Frame(win)
        login_logout_frame.pack(side=TOP, fill=X, anchor=CENTER)

        login_button_instance = Button(login_logout_frame, text='Login')
        logout_button_instance = Button(login_logout_frame, text='Logut')
        login_button_instance.configure(command=(lambda:
                                                 self.single_account_login(selected_account_object, logout_button_instance)))
        logout_button_instance.configure(command=(lambda:
                                                  self.single_account_logout(selected_account_object, login_button_instance)))
        logout_button_instance.pack(side=RIGHT)
        login_button_instance.pack(side=LEFT)
        if selected_account_object.authStatus != 'Logged In':
            logout_button_instance.configure(state='disable')
        elif selected_account_object.authStatus == 'Logged In':
            login_button_instance.configure(state='disable')

    def single_account_login(self, account_object, logout_button):
        account_object.login()
        if account_object.authStatus == 'Logged In':
            # account_object.start_thread(self.threaded_queue)
            self.recreate_tree()
            logout_button.configure(state='normal')
            self.place_order()
            self.loadPositionScreen()
            showinfo('Copy Trader', 'Logged in successfully')
        else:
            showerror('Copy Trader', 'Failed to login')

    def single_account_logout(self, account_object, login_button):
        account_object.logout()
        if account_object.authStatus == 'Logged Out':
            self.recreate_tree()
            login_button.configure(state='normal')
            self.place_order()
            self.loadPositionScreen()
            showinfo('Copy Trader', 'Logged out successfully')
        else:
            showerror('Copy Trader', 'Failed to logout')

    def remove_account(self, selected_account, account_screen):
        print(self.tree.get_children())
        if self.account_db.remove_account(selected_account.client_id) == True:
            if showinfo('Copy trader', 'Removed account {0} \n from copy trader'.format(selected_account)) == 'ok':
                selected_index = -1
                for ind, obj in enumerate(self.listOfAccounts):
                    if obj.client_id == selected_account.client_id:
                        selected_index = ind
                if selected_index != -1:
                    self.listOfAccounts.pop(selected_index)
                account_screen.destroy()
                self.recreate_tree()
            else:
                showerror('Copy trader', 'Failed to remove {0} \n from copy trader'.format(
                    selected_account))
        pass

    def recreate_tree(self):
        if len(self.tree.get_children()) != 0:
            self.remove_all_treeitems()
        pos = 1
        for acc in self.listOfAccounts:
            self.tree.insert('', 'end', text=pos, values=(acc.get_tree_view()))
            pos += 1

    def remove_all_treeitems(self):
        self.tree.delete(*self.tree.get_children())

    def loadInstruments(self):
        # name = askopenfilename(initialdir='.', filetypes=jsonTypes)
        # print(name)
        self.instrumentsData = json.load(
            open('/home/jayant/CT/ScripMaster.json'))

    def loadAccountInfo(self):
        self.listOfAccounts

    def setup_database(self):
        self.call_progressbar()

        self.order_db = Orders()
        self.angel_db = AngelInstruments()
        self.zerodha_db = ZerodhaInstruments()
        last_date = self.angel_db.check_last_update_date()

        # print(last_date,'last date',datetime.strptime(last_date[0][1],'%d-%m-%Y'),datetime.today(),datetime.today().strftime('%d-%m-%Y'))
        print(last_date, 'angel last date')
        if (len(last_date) == 0) or (len(last_date) != 0 and len(last_date[0]) != 0 and datetime.strptime(last_date[0][0], '%d-%m-%Y') < datetime.strptime(datetime.today().strftime('%d-%m-%Y'), '%d-%m-%Y')):
            self.initiate_instrument_data_fetch_angel()

        last_date = self.zerodha_db.check_last_update_date()
        print(last_date, 'zerodha last date')
        if (len(last_date) == 0) or (len(last_date) != 0 and len(last_date[0]) != 0 and datetime.strptime(last_date[0][0], '%d-%m-%Y') < datetime.strptime(datetime.today().strftime('%d-%m-%Y'), '%d-%m-%Y')):
            self.initiate_instrument_data_fetch_zerodha()

        self.stop_progressbar()

    def initiate_instrument_data_fetch_zerodha(self):
        retries = 0
        success = False
        while not success and retries < 3:
            try:
                dump_connection = http.client.HTTPSConnection("api.kite.trade")
                dump_connection.request(
                    'GET', constant.INSTRUMENTCSVDUMPZERODHA)
                res = dump_connection.getresponse()
                data = res.read()
                if res.status == 200:
                    success = True
                    recordsData = []
                    # try:
                    data_list = csv.reader(data.decode(
                        'utf-8').splitlines(), delimiter='\n')
                    # except ValueError:
                    #         raise print("Couldn't parse the JSON response received from the server: {content}".format(
                    #             content=data))
                # sampleRecords = [{"token":"12487","symbol":"CYIENT-BL","name":"CYIENT","expiry":"","strike":"-1.000000","lotsize":"1","instrumenttype":"","exch_seg":"NSE","tick_size":"5.000000"},{"token":"972","symbol":"64KA30C-SG","name":"64KA30C","expiry":"","strike":"-1.000000","lotsize":"100","instrumenttype":"","exch_seg":"NSE","tick_size":"1.000000"},{"token":"12718","symbol":"RIIL-BL","name":"RIIL","expiry":"","strike":"-1.000000","lotsize":"1","instrumenttype":"","exch_seg":"NSE","tick_size":"5.000000"},{"token":"10959","symbol":"749HP34-SG","name":"749HP34","expiry":"","strike":"-1.000000","lotsize":"100","instrumenttype":"","exch_seg":"NSE","tick_size":"1.000000"}]
                    for elem in list(data_list):
                        # print(elem.values())
                        # print(tuple(elem[0].split(',')),'tuple lelemnt',elem)
                        recordsData.append(tuple(elem[0].split(',')))
                    recordsDataRowCount = self.zerodha_db.insert_instruments_data(
                        recordsData)
                    print(recordsDataRowCount)
                    res = self.zerodha_db.insert_date_entry()
                    print(res, 'check 1 zerodha db insertion')
                    self.stop_progressbar()
                    success = True
                    return

            except Exception as e:
                print("Error occured", e)
                retries += 1

    def initiate_instrument_data_fetch_angel(self):
        retries = 0
        success = False
        while not success and retries < 3:
            try:
                dump_connection = http.client.HTTPSConnection(
                    "margincalculator.angelbroking.com")
                dump_connection.request('GET', constant.INSTRUMENTCSVDUMP)
                res = dump_connection.getresponse()

                data = res.read()
                # print(res.status, data)
                if res.status == 200:
                    success = True
                    recordsData = []
                    try:
                        data_list = json.loads(data)
                    except ValueError:
                        raise print("Couldn't parse the JSON response received from the server: {content}".format(
                            content=data))
                # sampleRecords = [{"token":"12487","symbol":"CYIENT-BL","name":"CYIENT","expiry":"","strike":"-1.000000","lotsize":"1","instrumenttype":"","exch_seg":"NSE","tick_size":"5.000000"},{"token":"972","symbol":"64KA30C-SG","name":"64KA30C","expiry":"","strike":"-1.000000","lotsize":"100","instrumenttype":"","exch_seg":"NSE","tick_size":"1.000000"},{"token":"12718","symbol":"RIIL-BL","name":"RIIL","expiry":"","strike":"-1.000000","lotsize":"1","instrumenttype":"","exch_seg":"NSE","tick_size":"5.000000"},{"token":"10959","symbol":"749HP34-SG","name":"749HP34","expiry":"","strike":"-1.000000","lotsize":"100","instrumenttype":"","exch_seg":"NSE","tick_size":"1.000000"}]
                    for elem in data_list:
                        recordsData.append((
                            elem['token'],
                            elem['symbol'],
                            elem['name'],
                            elem['expiry'],
                            elem['strike'],
                            elem['lotsize'],
                            elem['instrumenttype'],
                            elem['exch_seg'],
                            elem['tick_size']
                        ))
                    recordsDataRowCount = self.angel_db.insert_instruments_data(
                        recordsData)
                    print(recordsDataRowCount, res.status)
                    res = self.angel_db.insert_date_entry()
                    print(res, 'check 1 angel db insertion')
                    self.stop_progressbar()
                    success = True
                    return

            except Exception as e:
                print("Error occured", e)
                retries += 1

    def call_progressbar(self):
        # self.prog_bar = ProgressBarPanel(self.parent)
        # self.prog_bar.start_progress()
        pass

    def stop_progressbar(self):
        # self.prog_bar.stop_progress()
        # self.prog_bar.remove_bar()
        pass

    def setup_default_risk_profiles(self):
        self.order_risk_profile_var = []
        self.account_risk_profile_var = []
        rows, cols = (3, 3)
        self.risk_db = RiskProfile()
        default_risk_profile = self.risk_db.get_risk_profile_by_name(
            'default_name')
        print(default_risk_profile)
        try:
            if len(default_risk_profile) != 0 and len(default_risk_profile[0]) != 0:
                print(json.loads(default_risk_profile[0][0]))
                loaded_profiles = json.loads(default_risk_profile[0][0])
                for i in range(rows):
                    self.order_risk_profile_var.append([])
                    for j in range(cols):
                        self.order_risk_profile_var[i].append(
                            DoubleVar(value=loaded_profiles['order_risk'][i][j]))

                for i in range(3):
                    self.account_risk_profile_var.append(
                        DoubleVar(value=loaded_profiles['account_risk'][i]))

            else:
                for i in range(rows):
                    self.order_risk_profile_var.append([])
                    for j in range(cols):
                        self.order_risk_profile_var[i].append(
                            DoubleVar(value=(i*20)+(j*18) + 20))

                self.account_risk_profile_var = []
                pos = 33.3
                for i in range(3):
                    self.account_risk_profile_var.append(DoubleVar(value=pos))
                    pos += 33.3
        except Exception as e:
            print(e, 'An Exception occured')

    def add_risk_rules(self):
        win = Toplevel(self, padx=20, height=500, width=350,
                       pady=20)
        win.pack_propagate(0)
        win.title('Account Risk Rules')
        win.config()
        # prev_panel = LabelFrame(win, text='Risk Profiles', pady=5, padx=10, width=250)
        # list_of_risk_profiles = self.risk_db.get_risk_profile_names()
        #         # setting variable for Integers
        # # for elem in list_of_risk_profiles:

        # selected_risk_profiles = StringVar()
        # selected_risk_profiles.set(list_of_risk_profiles[0])
        # # creating widget
        # account_risk_option = OptionMenu(
        #     prev_panel,
        #     selected_risk_profiles,
        #     *list_of_risk_profiles
        # )
        # # positioning widget
        # account_risk_option.pack(expand=True)

        # prev_panel.pack(side=TOP, fill=X)
        risk_matrix = LabelFrame(
            win, text='Account risk x Order risk matrix', pady=5, padx=10, width=250)
        Label(risk_matrix, text='Current profile',
              pady=20, padx=10, width=250).pack(side=TOP, fill=X)
        Label(risk_matrix, text='Low <------ Accounts ------> High',
              pady=20, padx=10, width=250).pack(side=TOP, fill=X)
        # text_var = []
        entries = []
        label_frames = []
        rows, cols = (3, 3)
        for i in range(rows):
            # append an empty list to your two arrays
            # so you can append to those later
            entries.append([])
            label_frames.append(LabelFrame(
                risk_matrix, text=self.return_risk_label(i), pady=5, padx=5))
            label_frames[i].pack(side=TOP)
            Label(label_frames[i], text='Low').pack(side=LEFT)
            for j in range(cols):
                # append your StringVar and Entry
                entries[i].append(
                    Entry(label_frames[i], textvariable=self.order_risk_profile_var[i][j], width=5))
                # print(i, j)
                entries[i][j].pack(side=LEFT, anchor=self.return_anchor(i, j))
            Label(label_frames[i], text='High').pack(side=LEFT)

        # button= Button(risk_matrix,text="Submit", bg='bisque3', width=15,
        # command=(lambda : self.save_risk_profile(text_var=text_var)))
        # button.place(x=160,y=140)
        risk_matrix.pack(side=TOP, fill=X)
        risk_account = LabelFrame(
            win, text='Independent account level risk settings', pady=5, padx=10, width=120)
        Label(risk_account, text='Low ------ Medium ------ High',
              pady=2, padx=10).pack(side=TOP, fill=X)

        for i in range(3):
            Entry(risk_account, textvariable=self.account_risk_profile_var[i], width=10).pack(
                side=LEFT, anchor=W)
        risk_account.pack(side=TOP, fill=X)

        button = Button(win, text="Save", width=15,
                        command=(lambda: self.save_risk_profile(text_var=self.order_risk_profile_var, risk_window=win)))
        button.pack(side=BOTTOM, fill=None)
        win.grab_set()

    def return_risk_label(self, i):
        if i == 0:
            return 'High Risk orders'
        elif i == 1:
            return 'Medium Risk orders'
        elif i == 2:
            return 'Low Risk orders'

    def return_anchor(self, i, j):
        anchor = ''
        if i == 0:
            anchor = anchor + 'n'
            if j == 0:
                anchor = anchor + 'w'
            if j == 2:
                anchor = anchor + 'e'
        if i == 1:
            anchor = anchor + 'center'
            if j == 0:
                anchor = 'w'
            if j == 2:
                anchor = 'e'
        if i == 2:
            anchor = anchor + 's'
            if j == 0:
                anchor = anchor + 'w'
            if j == 2:
                anchor = anchor + 'e'
        return anchor

    def save_risk_profile(self, text_var, risk_window):
        matrix = []
        rows, cols = (3, 3)
        for i in range(rows):
            matrix.append([])
            for j in range(cols):
                print(float(text_var[i][j].get()) == 0, float(text_var[i][j].get()) > 100, int(
                    text_var[i][j].get()) < 0, int(text_var[i][j].get()))
                if int(text_var[i][j].get()) > 100 or int(text_var[i][j].get()) < 0:
                    showwarning('Copy Trader',
                                'Please enter a value within 0 to 100')
                    return
                matrix[i].append(text_var[i][j].get())

        order_matrix = []
        for i in range(3):
            if int(self.account_risk_profile_var[i].get()) > 100 or int(self.account_risk_profile_var[i].get()) < 0:
                showwarning('Copy Trader',
                            'Please enter a value within 0 to 100')
                return
            order_matrix.append(self.account_risk_profile_var[i].get())

        risk_profile = {
            'order_risk': matrix,
            'account_risk': order_matrix
        }
        print(json.dumps(risk_profile))
        if self.risk_db.update_risk_profile_by_name('default_name', json.dumps(risk_profile)):
            if showinfo('Copy Trader', 'Risk profile updated successfully') == 'ok':
                risk_window.destroy()
        else:
            showerror('Copy Trader', 'Failed to update risk profile')

    def addAccountScreen(self):
        self.is_single_accountValid = False
        self.broker = StringVar()
        self.broker.set('angel')
        win = Toplevel(self, height=600, width=500, padx=20,
                       pady=20)
        win.pack_propagate(0)
        win.title('Add Account')
        win.config()
        Button(win, text='Import Accounts from a CSV',
               command=self.loadAccounts).pack(side=TOP, fill=X)
        Label(win, text='OR', fg='black', pady=15).pack(fill=X, side=TOP)
        main_account_input_frame = LabelFrame(win,
                                              text='Add a single account', pady=10, padx=10)
        main_account_input_frame.pack(side=TOP, fill=X)
        broker = LabelFrame(main_account_input_frame, text='Broker', pady=5)
        broker.pack(side=TOP, fill=X)
        radio1 = Radiobutton(broker, text='Angel', command=(
            lambda: ()), variable=self.broker, value='angel')
        radio1.pack(side=LEFT, fill=X)
        radio2 = Radiobutton(broker, text='Zerodha', command=(
            lambda: ()), variable=self.broker, value='zerodha')
        radio2.pack(side=LEFT, fill=X)
        clinet_id = LabelFrame(main_account_input_frame, text='Client ID',
                               pady=5,
                               padx=5)
        clinet_id.pack(side=TOP, anchor=W)
        self.clinet_id_entry = Entry(clinet_id,
                                     text='Enter client ID')
        self.clinet_id_entry.pack(side=TOP, fill=X)
        password = LabelFrame(main_account_input_frame, text='Password',
                              pady=5,
                              padx=5)
        password.pack(side=TOP, anchor=W)
        self.password_entry = Entry(password,
                                    text='Enter password')
        self.password_entry.pack(side=TOP, fill=X)
        api_key = LabelFrame(main_account_input_frame, text='API key',
                             pady=5,
                             padx=5)
        api_key.pack(side=TOP, anchor=W)
        self.api_key_entry = Entry(api_key,
                                   text='Enter API key')
        self.api_key_entry.pack(side=TOP, fill=X)
        secret_key = LabelFrame(main_account_input_frame, text='Secret key',
                                pady=5,
                                padx=5)
        secret_key.pack(side=TOP, anchor=W)
        self.secret_key_entry = Entry(secret_key,
                                      text='Enter secret key')
        self.secret_key_entry.pack(side=TOP, fill=X)
        totp_key = LabelFrame(main_account_input_frame, text='TOTP key',
                              pady=5,
                              padx=5)
        totp_key.pack(side=TOP, anchor=W)
        self.totp_key_entry = Entry(totp_key,
                                    text='Enter TOTP key')
        self.totp_key_entry.pack(side=TOP, fill=X)

        account_level_risk = LabelFrame(main_account_input_frame, text='Account level risk',
                                        pady=5,
                                        padx=5)

        # setting variable for Integers
        self.account_risk = StringVar()
        self.account_risk.set(self.account_risk_vars[0])
        # creating widget
        account_risk_option = OptionMenu(
            account_level_risk,
            self.account_risk,
            *self.account_risk_vars,
            command=self.display_selected
        )
        # positioning widget
        account_risk_option.pack(expand=True)
        account_level_risk.pack(side=TOP, anchor=W)
        single_acc_save_btn = Button(
            main_account_input_frame, text='Save Account', command=(self.save_single_account))
        single_acc_save_btn.pack(side=RIGHT, anchor=SE)
        single_acc_save_btn.configure(state='disable')
        Button(main_account_input_frame, text='Test Account', command=(
            lambda: self.validate_single_account(single_acc_save_btn))).pack(side=RIGHT, anchor=SE)

    def display_selected(self, choice):
        choice = self.account_risk.get()
        print(choice)

    def validate_single_account(self, single_acc_btn):
        if self.broker.get() == '':
            showerror('Missing parameter', 'Please select a broker')
            return False
        if self.clinet_id_entry.get() == '':
            showerror('Missing parameter', 'Please Enter client ID')
            return False
        if self.password_entry.get() == '':
            showerror('Missing parameter', 'Please Enter the password')
            return False
        if self.totp_key_entry.get() == '':
            showerror('Missing parameter', 'Please Enter the TOTP key')
            return False
        if self.secret_key_entry.get() == '':
            showerror('Missing parameter', 'Please Enter the secret key')
            return False
        else:
            print('broker:{0}\nclient id:{1}\npassword:{2}\nsecret key:{3}\ntotp key:{4}'.format(self.broker.get(
            ), self.clinet_id_entry.get(), self.password_entry.get(), self.secret_key_entry.get(), self.totp_key_entry.get()))
            self.temp_account_object = Account(self.clinet_id_entry.get(), self.password_entry.get(
            ), self.api_key_entry.get(), self.secret_key_entry.get(), self.totp_key_entry.get(), self.broker.get(), self.account_risk.get())
            for x in self.listOfAccounts:
                if x.client_id == self.clinet_id_entry.get():
                    showerror('Account already exists',
                              'Please retry with a different client id')
                    return None

            # print(temp_account_object)
            self.temp_account_object.login()
            if self.temp_account_object.authStatus == 'Logged In':
                showinfo('Test Account Validated',
                         'You can now save this account')
                single_acc_btn.configure(state='normal')
            else:
                showerror('Test Account Validation Failed',
                          'Please recheck your credetials or try again later')

    def save_single_account(self):

        try:
            if self.temp_account_object.authStatus == 'Logged In':
                self.account_db.insert_account_single_entry(
                    self.temp_account_object.tuple_val())
                self.listOfAccounts.append(self.temp_account_object)
                self.recreate_tree()
                self.place_order()
                showinfo('Copy Trader',
                         'Account saved successfully')
        except Exception as e:
            print(e)
            showwarning('An error occured please try again or contact the admin',
                        e, parent=(self.master))

    def start_progress_bar(self):
        # self.progbar = ttk.Progressbar(self.parent, orient=HORIZONTAL, length=220, mode="indeterminate")
        # self.progbar.pack(pady=20)
        # self.progbar.start()
        pass

    def stop_progress_bar(self):
        # if self.progbar:
        #     self.progbar.stop()
        pass


if __name__ == '__main__':

    root = Tk()
    root.title('Copy Trader 1.0')
    root.iconname('CT')
    # Label(root, text="Copy Trader").pack()
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()

    CopyTraderGUI(root, bd=3, relief=SUNKEN)
    root.mainloop()
