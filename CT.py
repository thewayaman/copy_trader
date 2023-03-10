import fcntl
from tkinter import ttk
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
        self.style = ttk.Style(self.parent)
        self.style.theme_use(self.style.theme_names()[0])
        self.selectedInstrumentData = ''
        self.instruments = []
        self.listOfAccounts = []
        self.listOfXLSXAccounts = []
        self.account_risk_vars = ['Low', 'Medium', 'High']
        self.is_place_order_panel_initial_load = True
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
        self.menu.add_cascade(label='Order', menu=order)
        self.menu.add_command(label='Quit', command=self.onQuit)
        self.master.configure(menu=self.menu)

    def fetch(self):
        print('Input => "%s"' + self.clientcode.get())  # get text

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
        canvas = Canvas(self.place_order_var, borderwidth=0, background="#e0e0e0", width=210)
        accountSettingsFrame = LabelFrame(
            canvas, text='Selected Accounts', height=300, width=200, padx=2)
        accountSettingsFrame.pack(side=RIGHT, fill=Y)

        sbar = Scrollbar(self.place_order_var, orient="vertical", command=(canvas.yview))
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
        selectedInstrument = Frame(self.place_order_var, height=300, width=400, pady=2)
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

        combo_frame2 = Frame(self.place_order_var, pady=4)

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

        combo_frame2.pack(side=TOP, fill=X)

        quantity = Frame(self.place_order_var, height=300, width=100, padx=5, pady=4)
        labL = Label(quantity, width=5, text='Lot')
        self.entL = Entry(quantity, width=5, text='Lot size')
        labL.pack(side=LEFT)
        self.entL.pack(side=LEFT)
        self.entL.configure(state='normal')
        self.entL.delete(0, END)
        self.entL.insert(0, int(0))
        self.entL.configure(state='disable')
        labM = Label(quantity, width=10, text='Multiples')
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

        price_combo1 = Frame(self.place_order_var, height=300, width=100, padx=1, pady=5)
        labP = Label(price_combo1, width=5, text='Price')
        self.entP = Entry(price_combo1, width=10, text='Enter Price')
        labP.pack(side=LEFT)
        self.entP.pack(side=LEFT)
        price_combo1.pack(side=TOP, fill=X)

        labP = Label(price_combo1, width=10, text='Stop Loss')
        self.entSL = Entry(price_combo1, width=10, text='Enter Stop Loss')
        labP.pack(side=LEFT)
        self.entSL.pack(side=LEFT)
        price_combo1.pack(side=TOP, fill=X)

        btnsFrame = Frame(self.place_order_var, height=300, width=400, padx=5, pady=4)
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
                quantity_panel[elem].set(
                    round(float(0 if self.entM.get() == '' else self.entM.get())
                          * account_risk_matrix[risk_setting[elem]] / 100)
                )
                # print(
                #     elem,
                #     risk_setting[elem],
                #     self.entM.get(),
                #     account_risk_matrix[risk_setting[elem]],
                #     self.order_level_risk_category.get()
                # )

    def loadOrderScreen(self):
        win = Toplevel(self, height=550, width=900, padx=20,
                       pady=20)
        win.pack_propagate(0)
        win.title('Order')
        win.config()
        self.Ordercanvas = Canvas(win, borderwidth=0)
        self.Orderframe = Frame((self.Ordercanvas), width=700)
        self.vsb = Scrollbar(win, orient=VERTICAL,
                             command=(self.Ordercanvas.yview))
        self.Ordercanvas.configure(yscrollcommand=(self.vsb.set))
        self.vsb.pack(side=RIGHT, fill=Y)
        self.Ordercanvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.Orderframe.pack(side=LEFT, fill=BOTH, expand=True)
        self.Ordercanvas.create_window((4, 4), window=(
            self.Orderframe), anchor='nw', tags='self.Orderframe')
        self.Orderframe.bind('<Configure>', self.onFrameConfigure)
        for acc in self.listOfAccounts:
            accFrame = LabelFrame((self.Orderframe),
                                  height=300, width=700, text=(acc.client_id), pady=20)
            columns = ('INSTRUMENT', 'QUANTITY', 'PRICE', 'STATUS')
            acctree = ttk.Treeview(accFrame, columns=columns, show='headings')
            acctree.heading('INSTRUMENT', text='Instrument')
            acctree.heading('QUANTITY', text='Quantity')
            acctree.heading('PRICE', text='Price')
            acctree.heading('STATUS', text='Status')
            for acc in self.listOfAccounts:
                acctree.insert('', END, values=(acc.status()))
            else:
                accFrame.pack(side=TOP, fill=X, expand=True)
                acctree.pack(side=TOP, fill=X, expand=True)

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
            self.selectedInstrument.delete(0, END)
            self.selectedInstrument.insert(0, label)
            self.entL.configure(state="normal")
            self.entL.delete(0, END)
            self.entL.insert(0, int(instrument[5]))
            self.entL.configure(state="disable")
            self.multiplyLots(riskpanel, quantity_panel, risk_setting)
            self.selectedInstrumentData = instrument
            print("Selected", label,
                  instrument, instrument[5])
        except:
            self.selectedInstrumentData = ''
            print("An exception occurred")

    def get_last_traded_price(self):
        pass

    def execute_order(self, accounts_object, quantity_panel, risk_panel, window_pane):
        for e in accounts_object.values():
            print(e.get(), 'iteration')

        index = self.listBoxOfInstruments.curselection()
        if len(index) == 0:
            showwarning(
                'Copy Trader', 'Please select an instrument to proceed', master=window_pane)
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
            'squareoff': '0',
            'stoploss': '0',
            'quantity': self.entQ.get()
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
        self.post_order_execeution_screen(post_order_success, 'Order Screen')
        self.recreate_tree()
    def post_order_execeution_screen(self, accounts_order_object, title_action):
        win = Toplevel(self, height=500, width=300, padx=20,
                       pady=20)
        win.pack_propagate(0)
        print(title_action, '482')
        win.title(title_action)
        win.config()
        for key, value in accounts_order_object.items():
            key_label = LabelFrame(win, text=key, padx=5, pady=5)
            key_label.pack(side=TOP, anchor=CENTER)
            Label(key_label, text=value).pack(side=TOP, anchor=CENTER)

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
                self.post_order_execeution_screen(loaded_accounts_object, 'Accounts')
                self.recreate_tree()
            except Exception as e :
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
                   selected_account=selected_account_object,account_screen=win))
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
            self.recreate_tree()
            logout_button.configure(state='normal')
            showinfo('Copy Trader', 'Logged in successfully')
            self.place_order()
        else:
            showerror('Copy Trader', 'Failed to login')

    def single_account_logout(self, account_object, login_button):
        account_object.logout()
        if account_object.authStatus == 'Logged Out':
            self.recreate_tree()
            login_button.configure(state='normal')
            showinfo('Copy Trader', 'Logged out successfully')
            self.place_order()
        else:
            showerror('Copy Trader', 'Failed to logout')

    def remove_account(self, selected_account,account_screen):
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
                # self.
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
