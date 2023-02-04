import fcntl
from tkinter import ttk
from requests import get
import http.client
import json
import mimetypes
from tkinter import *
from glob import glob
from tkinter.messagebox import askyesno
from tkinter.filedialog import askopenfilename
import random
import socket
import struct
import uuid
import constant
from openpyxl import load_workbook
from account import Account
from angel_db import AngelInstruments
from zerodha_db import ZerodhaInstruments
from datetime import datetime
from progress_bar import ProgressBarPanel
import csv
import queue

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
        self.style = ttk.Style(self.parent)
        print(self.style.theme_names(),'themes')
        self.style.theme_use(self.style.theme_names()[0])
        self.selectedInstrumentData = ''
        self.instruments = []
        self.listOfAccounts = []
        self.listOfXLSXAccounts = []
        self.loadAccounts()
        self.makeWidgets()
        # self.loadInstruments()
        self.createListOfAccountsWidget()
        self.setup_database()
        self.pack(expand=YES, fill=BOTH)
        self.queue = queue
        files = []
        self.msecs = msecs
        self.beep = 1
        self.drawn = None

    def makeWidgets(self):

        self.canvas = Frame(self, height=Height, width=Width)
        self.canvas.pack_propagate(0)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES, padx=5, pady=5)
        # self.accountFormPanel = Frame(self.canvas, height=225, width=Width)
        # self.accountFormPanel.pack(side=TOP, fill=NONE, expand=YES)
        # self.clientcode = Entry(self.accountFormPanel, width=20)
        # self.clientcode.insert(0, 'Enter client Code')  # set text
        # self.clientcode.pack(side=TOP)  # grow horiz
        # self.password = Entry(self.accountFormPanel, width=20)
        # self.password.insert(0, 'Enter password')  # set text
        # self.password.pack(side=TOP)  # grow horiz
        # self.totp = Entry(self.accountFormPanel, width=20)
        # self.totp.insert(0, 'Enter totp')  # set text
        # self.totp.pack(side=TOP)  # grow horiz
        # # self.clientcode.focus() # save a click
        # # self.clientcode.bind('<Enter>', (lambda event: self.fetch())) # on enter key
        # vBtn = Button(self.accountFormPanel, text='Valdiate',
        #               command=self.loginTest)  # and on button
        # vBtn.pack(side=LEFT)
        # aBtn = Button(self.accountFormPanel, text='Add', command=self.fetch)
        # aBtn.pack(side=RIGHT)

        self.onoff = Button(self, text='Configure', command=self.onStart)
        self.onoff.pack(fill=X)
        Button(self, text='Place Order', command=self.placeOrder).pack(fill=X)
        Button(self, text='Orders', command=self.loadOrderScreen).pack(fill=X)
        Button(self, text='Quit', command=self.onQuit).pack(fill=X)

    def onStart(self):
        # self.loop = 1
        self.onoff.config(text='Stop', command=self.onStop)
        self.canvas.config(height=Height, width=Width)
        self.onTimer()

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

    def placeOrder(self):
        self.call_progressbar()
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
        self.exchange.set('NSE')

        win = Toplevel(self, height=550, width=800,
                       padx=20, pady=20)  # new window
        win.pack_propagate(0)
        win.title('Order')  # set border
        win.config()
        # win.protocol('WM_DELETE_WINDOW', lambda:0) # ignore close

        """ INSTRUMENT SELECTION PANE STARTS """

        Isearch = Frame(win, height=300, width=400, pady=2)
        # add label, entry
        labI = Label(Isearch, width=15, text='Search Instrument')
        self.searchInstrumentItem = Entry(Isearch, width=40)
        self.searchInstrumentItem.bind(
            '<KeyRelease>', (lambda event: self.searchInstruments()))
        Isearch.pack(side=TOP)  # pack row on top
        labI.pack(side=LEFT)
        self.searchInstrumentItem.pack(
            side=LEFT, expand=YES)  # grow horizontal

        instrument = Frame(win, height=300, width=400)
        labI = Label(instrument, width=20, text='Instruments')
        sbar = Scrollbar(instrument)
        self.listBoxOfInstruments = Listbox(
            instrument, relief=SUNKEN, selectmode=SINGLE, exportselection=False)
        # xlink sbar and list
        sbar.config(command=self.listBoxOfInstruments.yview)
        self.listBoxOfInstruments.config(
            yscrollcommand=sbar.set)  # move one moves other
        sbar.pack(side=RIGHT, fill=Y)  # pack first=clip last
        labI.pack(side=TOP, expand=None, fill=X)
        self.listBoxOfInstruments.pack(
            side=LEFT, expand=YES, fill=BOTH)  # list clipped first
        instrument.pack(side=TOP, fill=X)  # pack row on top
        # pos = 0
        db_instrument_list = self.angel_db.get_instruments_data()
        self.instrumentsData = db_instrument_list
        # print(db_instrument_list)
        if len(db_instrument_list) != 0:
            for instrument in db_instrument_list:  # add to list-box
                self.listBoxOfInstruments.insert(
                    END, instrument[1])  # or insert(END,label)
            # pos = pos + 1
        
        self.listBoxOfInstruments.bind('<Button-1>', self.selectInstrument)

        selectedInstrument = Frame(win, height=300, width=400, pady=2)
        labP = Label(selectedInstrument, width=20,
                     text='Selected Instrument')  # add label, entry
        self.selectedInstrument = Entry(
            selectedInstrument, width=40, text='Selected Instrument')
        selectedInstrument.pack(side=TOP)  # pack row on top
        labP.pack(side=LEFT)
        self.selectedInstrument.pack(side=LEFT, expand=YES)

        """ INSTRUMENT SELECTION PANE ENDS """

        exchange = LabelFrame(win, height=300, width=400, text='Exchange')
        exchange.pack(side=TOP, fill=X)
        radio1 = Radiobutton(exchange, text="BSE Equity", command=(lambda: self.orderType()), variable=self.exchange,
                             value='BSE')
        radio1.pack(side=LEFT)
        radio2 = Radiobutton(exchange, text="NSE Equity", command=(lambda: self.orderType()), variable=self.exchange,
                             value='NSE')
        radio2.pack(side=LEFT)
        radio3 = Radiobutton(exchange, text="NSE Future and Options", command=(lambda: self.orderType()), variable=self.exchange,
                             value='NFO')
        radio3.pack(side=LEFT)

        buySellFrame = LabelFrame(win, height=300, width=200, text='Buy/Sell')
        buySellFrame.pack(side=TOP, fill=X)
        radio1 = Radiobutton(buySellFrame, text="Buy", command=(lambda: self.orderType()), variable=self.transactiontype,
                             value='BUY')
        radio1.pack(side=LEFT)
        radio2 = Radiobutton(buySellFrame, text="Sell", command=(lambda: self.orderType()), variable=self.transactiontype,
                             value='SELL')
        radio2.pack(side=LEFT)

        orderType = LabelFrame(win, height=300, width=200, text='Order type')
        orderType.pack(side=TOP, fill=X)
        rad1 = Radiobutton(orderType, text="Market", command=(lambda: self.orderType()), variable=self.ordertype,
                           value='MARKET')
        rad1.pack(side=LEFT)
        rad2 = Radiobutton(orderType, text="Limit", command=(lambda: self.orderType()), variable=self.ordertype,
                           value='LIMIT')
        rad2.pack(side=LEFT)

        producttype = LabelFrame(
            win, height=300, width=400, text='Product type')
        producttype.pack(side=TOP, fill=X)
        rad1 = Radiobutton(producttype, text="Cash & Carry for equity (CNC)", command=(lambda: self.orderType()), variable=self.producttype,
                           value='DELIVERY')
        rad1.pack(side=LEFT)
        rad2 = Radiobutton(producttype, text="Normal for futures and options (NRML)", command=(lambda: self.orderType()), variable=self.producttype,
                           value='CARRYFORWARD')
        rad2.pack(side=LEFT)
        rad3 = Radiobutton(producttype, text="Margin Intraday Squareoff (MIS)", command=(lambda: self.orderType()), variable=self.producttype,
                           value='INTRADAY')
        rad3.pack(side=LEFT)

        quantity = Frame(win, height=300, width=100, padx=5, pady=4)
        labL = Label(quantity, width=5, text='Lot')  # add label, entry
        self.entL = Entry(quantity, width=5, text='Lot size')
        # quantity.pack(side=TOP, fill=X) # pack row on top
        labL.pack(side=LEFT)
        self.entL.pack(side=LEFT)  # grow horizontal
        self.entL.configure(state="normal")
        self.entL.delete(0, END)
        self.entL.insert(0, int(0))
        self.entL.configure(state="disable")

        labM = Label(quantity, width=10, text='Multiples')  # add label, entry
        current_value_quant = StringVar(value=1)
        self.entM = Spinbox(quantity, from_=0, to=50, values=(0, 10, 20, 30, 40, 50), width=5,
                            textvariable=current_value_quant, wrap=False, command=self.multiplyLots)
        self.entM.bind('<KeyRelease>', self.btnClickMultiplyLots)
        labM.pack(side=LEFT)
        self.entM.pack(side=LEFT)  # grow horizontal

        # add label, entry
        labQ = Label(quantity, width=15, text='Total Quantity')
        self.entQ = Entry(quantity, width=10, text='Total Quantity')
        # quantity.pack(side=TOP, fill=X) # pack row on top
        labQ.pack(side=LEFT)
        self.entQ.pack(side=LEFT)  # grow horizontal

        # price = Frame(win,height=300,width=400,padx=20, pady=4)
        labP = Label(quantity, width=10, text='Price')  # add label, entry
        self.entP = Entry(quantity, width=10, text='Enter Price')
        # price.pack(side=TOP, fill=X) # pack row on top
        labP.pack(side=LEFT)
        self.entP.pack(side=LEFT)  # grow horizontal

        quantity.pack(side=TOP, fill=X)  # pack row on top

        btnsFrame = Frame(win, height=300, width=400, padx=20, pady=4)
        confirmBtn = Button(btnsFrame, text='Confirm',
                            command=(lambda: self.executeOrder()))
        cancelBtn = Button(btnsFrame, text='Cancel', command=())
        btnsFrame.pack(side=TOP, fill=X)
        confirmBtn.pack(side=LEFT, pady=4, padx=4)
        cancelBtn.pack(side=LEFT, pady=4, padx=4)
        self.stop_progressbar()

    def multiplyLots(self):
        if self.entM.get() != '' and self.entL.get() != '':
            print(type(self.entM.get()), type(self.entL.get()))
            self.entQ.delete(0, END)
            self.entQ.insert(0, int(float(self.entM.get()))
                             * int(float(self.entL.get())))

    def loadOrderScreen(self):
        win = Toplevel(self, height=550, width=900,
                       padx=20, pady=20)  # new window
        win.pack_propagate(0)
        win.title('Order')  # set border
        win.config()
        self.Ordercanvas = Canvas(win, borderwidth=0)
        # self.Ordercanvas.after(3000,self.rerenderOrderFrame)
        self.Orderframe = Frame(self.Ordercanvas, width=700)
        self.vsb = Scrollbar(win, orient=VERTICAL,
                             command=self.Ordercanvas.yview)
        self.Ordercanvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side=RIGHT, fill=Y)

        self.Ordercanvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.Orderframe.pack(side=LEFT, fill=BOTH, expand=True)

        self.Ordercanvas.create_window((4, 4), window=self.Orderframe, anchor="nw",
                                       tags="self.Orderframe")

        self.Orderframe.bind("<Configure>", self.onFrameConfigure)

        for acc in self.listOfAccounts:
            accFrame = LabelFrame(
                self.Orderframe, height=300, width=700, text=acc.client_id, pady=20)
            columns = ('INSTRUMENT', 'QUANTITY', 'PRICE', 'STATUS')
            acctree = ttk.Treeview(accFrame, columns=columns, show='headings')
            acctree.heading('INSTRUMENT', text='Instrument')
            acctree.heading('QUANTITY', text='Quantity')
            acctree.heading('PRICE', text='Price')
            acctree.heading('STATUS', text='Status')
            # col_width = acctree.winfo_width()
            # for acc in acctree['columns']:
            #     acctree.column(acc, anchor=CENTER, width=col_width)
            for acc in self.listOfAccounts:
                acctree.insert('', END, values=acc.status())
            accFrame.pack(side=TOP, fill=X, expand=True)
            acctree.pack(side=TOP, fill=X, expand=True)
        # self.initiateSocketConnections()

    def rerenderOrderFrame(self):
        print('rerenderOrderFrame')
        if self.Orderframe is not None:
            self.Orderframe.destroy()
        self.Orderframe = Frame(self.Ordercanvas, width=700)
        self.Orderframe.pack(side=LEFT, fill=BOTH, expand=True)
        for acc in self.listOfAccounts:
            accFrame = LabelFrame(
                self.Orderframe, height=300, width=700, text=acc.client_id, pady=20)
            columns = ('INSTRUMENT', 'QUANTITY', 'PRICE', 'STATUS')
            acctree = ttk.Treeview(accFrame, columns=columns, show='headings')
            acctree.heading('INSTRUMENT', text='Instrument1')
            acctree.heading('QUANTITY', text='Quantity2')
            acctree.heading('PRICE', text='Price3')
            acctree.heading('STATUS', text='Status4')
            col_width = acctree.winfo_width()
            # for acc in acctree['columns']:
            #     acctree.column(acc, anchor=CENTER, width=col_width)
            for acc in self.listOfAccounts:
                acctree.insert('', END, values=acc.status())
            accFrame.pack(side=TOP, fill=X, expand=True)
            acctree.pack(side=TOP, fill=X, expand=True)
        self.Ordercanvas.after(3000, self.rerenderOrderFrame)

    def btnClickMultiplyLots(self, event):
        if self.entM.get() != '' and self.entL.get() != '':
            print(type(self.entM.get()), type(self.entL.get()))
            self.entQ.delete(0, END)
            self.entQ.insert(0, int(float(self.entM.get()))
                             * int(float(self.entL.get())))

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.Ordercanvas.configure(scrollregion=self.Ordercanvas.bbox("all"))

    def selectInstrument(self, event):
        try:
            index = self.listBoxOfInstruments.curselection()  # on list double-click
            label = self.listBoxOfInstruments.get(index)
            instrument = ''
            for itme in [k for k in self.instrumentsData if label == k[1]]:
                print(itme,'405')
                instrument = itme
            # print(self.instrumentsData[index[0]])
            self.selectedInstrument.delete(0, END)
            self.selectedInstrument.insert(0, label)
            self.entL.configure(state="normal")
            self.entL.delete(0, END)
            self.entL.insert(0, instrument[5])
            self.entL.configure(state="disable")
            self.multiplyLots()
            self.selectedInstrumentData = instrument
            print("Selected", label,
                  instrument, instrument[5])
        except:
            self.selectedInstrumentData = ''
            print("An exception occurred")

    def executeOrder(self):
        index = self.listBoxOfInstruments.curselection()  # on list double-click
        label = self.listBoxOfInstruments.get(index)
        instrument = ''
        for itme in [k for k in self.instrumentsData if label == k[1]]:
            print(itme,'405')
            instrument = itme
        print("Order :\n"
              "  variety = {0}\n"
              "  transactiontype = {1}\n"
              "  ordertype = {2}\n"
              "  producttype = {3} \n"
              "  duration = {4} \n"
              "  exchange = {5} \n"
              "  price = {6} \n"
              "  quantity = {7} \n"
              "  selected Instrument = {8} \n"
              "  symboltoken = {9} \n"
              "  tradingsymbol = {10} \n".format(
                  self.variety.get(),
                  self.transactiontype.get(),
                  self.ordertype.get(),
                  self.producttype.get(),
                  self.duration.get(),
                  self.exchange.get(),
                  self.entP.get(),
                  self.entM.get(),
                  instrument[2],
                  instrument[1],
                  instrument[0]
              ))
        orderObject = {
            "variety": self.variety.get(),
            "tradingsymbol": instrument[1],
            "symboltoken": instrument[0],
            "transactiontype": self.transactiontype.get(),
            "exchange": self.exchange.get(),
            "ordertype": self.ordertype.get(),
            "producttype": self.producttype.get(),
            "duration": self.duration.get(),
            "price": self.entP.get(),
            "squareoff": "0",
            "stoploss": "0",
            "quantity": self.entM.get()
        }
        print(orderObject)
        for acc in self.listOfAccounts:
            if acc.get_auth_status() == 'Logged In':
                acc.place_order(orderObject)
            else:
                acc.place_order(orderObject)
                pass
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
        self.onStop()
        self.update()
        if askyesno('PyView', 'Really quit now?'):
            for item in self.listOfAccounts:
                if item.is_valid():
                    item.logout()
            self.quit()

    def fetchUserProfile():
        print('')

    def loadAccounts(self):
        # name = askopenfilename(initialdir='.', filetypes=sheetTypes)
        name = '/home/jayant/Desktop/Accounts.xlsx'
        print(name)
        if name:
            wb = load_workbook(name)
            ws = wb[wb.sheetnames[0]]
            # items = []
            for idx, row in enumerate(ws.rows):
                if idx != 0:
                    values = []
                    for cell in row:
                        print(cell.value)
                        values.append(cell.value)
                    print(values)
                    self.listOfXLSXAccounts.append(values)
                    acc = Account(*values)
                    self.listOfAccounts.append(acc)
            # Close the workbook after reading
            wb.close()
            for item in self.listOfAccounts:
                print(item)
                if acc.is_valid():
                    # item.login()
                    item.get_user_profile()
                    # item.wstest()
                # print("Accessing one single value (eg. CLIENT_ID): {0}".format(
                #     item.client_id))
                # print
        # df = pandas.read_excel('Accounts.xlsx')

    def initiateSocketConnections(self):
        for item in self.listOfAccounts:
            print(item)
            if item.is_valid():
                item.initiate_socket_connection()
            print("Accessing one single value (eg. CLIENT_ID): {0}".format(
                item.client_id))

    def createListOfAccountsWidget(self):
        # Add a Treeview widget and set the selection mode
        self.tree = ttk.Treeview(self.canvas, column=('CLIENT_ID', 'PASSWORD', 'APIKEY',
                   'SECRETKEY', 'TOTPKEY', 'STATUS'), show='headings', height=8, selectmode="browse")
        self.tree.heading('CLIENT_ID', text='Client ID')
        self.tree.heading('PASSWORD', text='Password')
        self.tree.heading('APIKEY', text='API key')
        self.tree.heading('SECRETKEY', text='Secret key')
        self.tree.heading('TOTPKEY', text='TOTP key')
        self.tree.heading('STATUS', text='Status')

        # Insert the data in Treeview widget
        pos = 1
        col_width = self.tree.winfo_width()
        for acc in self.tree['columns']:
            self.tree.column(acc, anchor=CENTER, width=col_width)
        for acc in self.listOfAccounts:
            self.tree.insert('', 'end',text=pos,values=acc.status())
            pos+=1

        # Adding a vertical scrollbar to Treeview widget
        treeScroll = ttk.Scrollbar(self.canvas)
        treeScroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treeScroll.set)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        treeScroll.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT,fill=BOTH,expand=True)

    def OnDoubleClick(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if self.tree.item(item) != '' and self.tree.item(item)['values']:
            selectedItem = self.tree.item(item)['values']
            print("you clicked on", [
                  x for x in self.listOfAccounts if x.client_id == selectedItem[0]])

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
        print(last_date,'angel last date')
        if (len(last_date) == 0) or (len(last_date) != 0 and len(last_date[0]) != 0 and datetime.strptime(last_date[0][0],'%d-%m-%Y')<datetime.strptime(datetime.today().strftime('%d-%m-%Y'),'%d-%m-%Y')):
            self.initiate_instrument_data_fetch_angel()
            res = self.angel_db.insert_date_entry()
            print(res,'check 1 angel db insertion')
        
        last_date = self.zerodha_db.check_last_update_date()
        print(last_date,'zerodha last date')
        if (len(last_date) == 0) or (len(last_date) != 0 and len(last_date[0]) != 0 and datetime.strptime(last_date[0][0],'%d-%m-%Y')<datetime.strptime(datetime.today().strftime('%d-%m-%Y'),'%d-%m-%Y')):
            self.initiate_instrument_data_fetch_zerodha()
            res = self.zerodha_db.insert_date_entry()
            print(res,'check 1 zerodha db insertion')
        self.stop_progressbar()
    def initiate_instrument_data_fetch_zerodha(self):
        retries = 0
        success = False
        while not success and retries < 3:
            try:
                dump_connection = http.client.HTTPSConnection("api.kite.trade")
                dump_connection.request('GET',constant.INSTRUMENTCSVDUMPZERODHA)
                res = dump_connection.getresponse()
                data = res.read()
                if res.status == 200:
                    success = True
                    recordsData =[]
                    # try:
                    data_list = csv.reader(data.decode('utf-8').splitlines(), delimiter='\n')
                    # except ValueError:
                    #         raise print("Couldn't parse the JSON response received from the server: {content}".format(
                    #             content=data))
                # sampleRecords = [{"token":"12487","symbol":"CYIENT-BL","name":"CYIENT","expiry":"","strike":"-1.000000","lotsize":"1","instrumenttype":"","exch_seg":"NSE","tick_size":"5.000000"},{"token":"972","symbol":"64KA30C-SG","name":"64KA30C","expiry":"","strike":"-1.000000","lotsize":"100","instrumenttype":"","exch_seg":"NSE","tick_size":"1.000000"},{"token":"12718","symbol":"RIIL-BL","name":"RIIL","expiry":"","strike":"-1.000000","lotsize":"1","instrumenttype":"","exch_seg":"NSE","tick_size":"5.000000"},{"token":"10959","symbol":"749HP34-SG","name":"749HP34","expiry":"","strike":"-1.000000","lotsize":"100","instrumenttype":"","exch_seg":"NSE","tick_size":"1.000000"}]
                    for elem in list(data_list):
                        # print(elem.values())
                        # print(tuple(elem[0].split(',')),'tuple lelemnt',elem)
                        recordsData.append(tuple(elem[0].split(',')))
                    recordsDataRowCount = self.zerodha_db.insert_instruments_data(recordsData)
                    print(recordsDataRowCount)
                    self.stop_progressbar()
                    success = True
                    return
                
            except ValueError:
                print("Error occured")
                retries +=1
    def initiate_instrument_data_fetch_angel(self):
        retries = 0
        success = False
        while not success and retries < 3:
            try:
                dump_connection = http.client.HTTPSConnection("margincalculator.angelbroking.com")
                dump_connection.request('GET',constant.INSTRUMENTCSVDUMP)
                res = dump_connection.getresponse()
                
                data = res.read()
                # print(res.status, data)
                if res.status == 200:
                    success = True
                    recordsData =[]
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
                    recordsDataRowCount = self.angel_db.insert_instruments_data(recordsData)
                    print(recordsDataRowCount,res.status)
                    self.stop_progressbar()
                    success = True
                    return
                
            except ValueError:
                print("Error occured")
                retries +=1

    def call_progressbar(self):
        # self.prog_bar = ProgressBarPanel(self.parent)
        # self.prog_bar.start_progress()
        pass
    def stop_progressbar(self):
        # self.prog_bar.stop_progress()
        # self.prog_bar.remove_bar()
        pass

if __name__ == '__main__':

    root = Tk()
#  root.attributes('-fullscreen', True)
    root.title('Copy Trader 1.0')
    root.iconname('CT')
    Label(root, text="Copy Trader").pack()
    CopyTraderGUI(root, bd=3, relief=SUNKEN)
    root.mainloop()
