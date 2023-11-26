import http.client
import json
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta

if __name__ == '__main__':
    CONNECTION = "postgresql://postgres:bbking@172.19.0.1:5432"
    
    symbolMapper = {
        # 'ICICIBANK':'1270529',
        # 'KOTAKBANK':'492033',
        # 'SBIN':'779521',
        # 'HINDUNILVR':'356865',
        # 'ITC':'424961',
        # 'JSWSTEEL':'3001089',
        # 'ULTRACEMCO':'2952193',
        # 'DRREDDY':'225537',
        # 'LALPATHLAB':'2983425',
        # 'APOLLOHOSP':'40193',
        # 'SUNPHARMA':'857857',
        # 'HDFCLIFE':'119553',
        # 'HAVELLS':'2513665',
        # 'VOLTAS':'951809',
        # 'GAIL':'1207553',
        # 'IGL':'2883073',
        # 'BHARTIARTL':'2714625',
        # 'ASIANPAINT':'60417',
        # 'NTPC':'2977281',
        # 'SRF':'837889',
        # 'PIIND':'6191105',
        # 'NAVINFLUOR':'3756033',
        # 'MUTHOOTFIN':'6054401',
        # 'BAJFINANCE':'81153',
        # 'MANDM':'519937',
        # 'MARUTI':'2815745',
        'BAJAJ_AUTO':'4267265',
        'TATAMOTORS':'884737',
        'INFY':'408065',
        'TCS':'2953217',
        'BPCL':'134657',
        'TATACHEM':'871681',
        'INDIGO':'2865921',
        'LT':'2939649',
        'ABB':'3329',
        'COALINDIA':'5215745'
    }
    
    for key  in symbolMapper:   
        with psycopg2.connect(CONNECTION) as conn:
            try:
                print(key,symbolMapper[key])
                SYMBOL_NAME = key
                SYMBOL_TOKEN = symbolMapper[key]
                create_table_query = """CREATE TABLE {0} (
                                                time TIMESTAMP NOT NULL,
                                                open DOUBLE PRECISION,
                                                high DOUBLE PRECISION,
                                                low DOUBLE PRECISION,
                                                close DOUBLE PRECISION,
                                                volume DOUBLE PRECISION,
                                                oi DOUBLE PRECISION
                                            );
                                            """.format(SYMBOL_NAME)
                
                cursor = conn.cursor()
                try:
                    cursor.execute(create_table_query)
                except Error as e:
                    print('Table creation',e)
                # use the cursor to interact with your database
                # cursor.execute(create_table_query)
                # cursor.execute("SELECT create_hypertable('nifty', 'time');")
                conn.commit()
                from_date = '1996-01-15+09:15:00'
                # from_date = '2022-01-15+09:15:00'
                print(datetime.strptime(from_date, "%Y-%m-%d+%H:%M:%S") < datetime.today())
                cursor = conn.cursor()
                query = "SELECT * FROM {0};".format(SYMBOL_NAME)
                print(cursor.execute(query))
                while datetime.strptime(from_date, "%Y-%m-%d+%H:%M:%S") < datetime.today():
                    #     # execute_logic
                    print(from_date)

                    to_date = '+'.join(str(datetime.strptime(from_date,
                                    "%Y-%m-%d+%H:%M:%S") + timedelta(days=30)).split(' '))
                    try:
                        headers = {}
                        auth_header = "lef83s9j4x3xp940:02UOM3dDpC1nVB8gf5bdwMPrt8QXpP5Z"
                        headers["Authorization"] = "token {}".format(auth_header)
                        headers["X-Kite-Version"] = "3"
                        print(headers,'/instruments/historical/{2}/minute?from={0}&to={1}'.format(from_date, to_date,SYMBOL_TOKEN))
                        conn = http.client.HTTPSConnection("api.kite.trade")

                        conn.request("GET", '/instruments/historical/{2}/minute?from={0}&to={1}&oi=1'.format(from_date, to_date,SYMBOL_TOKEN), {},
                                    headers)
                        res = conn.getresponse()
                        data = res.read()
                        from_date = to_date
                        print(res.status, data.decode("utf-8"))
                        if res.status == 200:
                            retries = 5
                            parsedJson = json.loads(data.decode("utf-8"))
                            print(res.status,parsedJson['data']['candles'][0])
                            if 'errorcode' in parsedJson and parsedJson['errorcode'] != '':
                                print(parsedJson['errorcode'])
                            else:
                                # print(parsedJson, 'Final parsed json get_positions_zerodha')
                                if parsedJson['status'] == 'success' and type(parsedJson['data']['candles']) is list:
                                    try:
                                        for candle in parsedJson['data']['candles']:
                                            cursor.execute("INSERT INTO {0} (time,open,high,low,close,volume,oi) VALUES (%s,%s,%s,%s,%s,%s,%s);".format(SYMBOL_NAME),(candle[0], candle[1],candle[2],candle[3],candle[4],candle[5],candle[6]))
                                            # print(candle[0], candle[1],candle[2],candle[3],candle[4],candle[5],candle[6],'\n')
                                    except (Exception, psycopg2.Error) as error:
                                        print(error)
                                    # pass    
                        else:
                            break
                    except Exception as e:
                        print(
                            "Couldn't parse the JSON response received from the server: {0}".format(e))
            except Error as e:
                print('For loop broken',e)