from pymongo import MongoClient
from client import TradeClient, Client
import time
import sys
sys.path.append('../')
import config

bfxclient = Client()

order = MongoClient().wtracker.orders
no_active_trade = MongoClient().wtracker.trade

def get_active_positions():
    bfx = TradeClient(config.key,config.secret)
    return bfx.active_positions()

while(1):
    active_positions = get_active_positions()

    if not active_positions:
       time.sleep(300)
       continue

    buy = []
    sell = []
    tot_pl = 0
    for x in active_positions:
        tot_pl += x["pl"]

    if tot_pl > 0:
        for x in active_positions:
            amount = float(x["amount"])

            if amount > 0:
                # long position
                bfx = TradeClient(config.key,config.secret)
                execute = bfx.place_order(amount * -1, "1", "sell", "market", x["symbol"])

            elif amount < 0:
                bfx = TradeClient(config.key,config.secret)
                execute = bfx.place_order(amount * -1, "1", "buy", "market", x["symbol"])

        print("sold everything")
        
    time.sleep(60)