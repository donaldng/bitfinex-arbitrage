from pymongo import MongoClient
from public import get_host, get_port
from websocket import create_connection
import time, json, os, sys
import config


try:
    pid = int(sys.argv[2]) if len(sys.argv) == 3 else 0
    pair = sys.argv[1]
except:
    print('Please pass in correct parameter, crypto pair required! E.g. BTCUSD or ETHBTC')

    
db = MongoClient(get_host(), get_port()).wtracker

ws = create_connection('wss://api.bitfinex.com/ws/')
sub = json.dumps({'event': 'subscribe', 'channel': 'trades', 'pair':pair})
ws.send(sub)

while True:
    x = json.loads(ws.recv())

    if pid:
        try:
            os.kill(pid, 0)
        except:
            sys.exit()

    if len(x) == 6:
        ts = x[3]
        price = x[4]
        amount = x[5]
        base = 1 if pair == "BTCUSD" or pair == "ETHUSD" else 0

        if amount % 10:
            data = {'ts':ts, 'price': price,'amount':amount, 'pair': pair, 'base': base}
            res = db.trades.insert_one(data)

ws.close()