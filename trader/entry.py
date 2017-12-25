from pymongo import MongoClient
from client import TradeClient, Client
import time
import sys
sys.path.append('../')
import config

bfxclient = Client()

order = MongoClient().wtracker.orders
no_active_trade = MongoClient().wtracker.trade
lookback = 1

def get_active_positions():
    bfx = TradeClient(config.key,config.secret)
    return bfx.active_positions()


while(1):

    active_positions = get_active_positions()

    if active_positions:
       time.sleep(600)
       continue

    t = int(time.time())-lookback
    cur = order.find( { 'ts' : { '$gt' : t } } )
    order.delete_many( { 'ts' : { '$lt' : t-lookback } } )

    # look for most expensive in asks.
    # look for cheapest in bids.
    group = {}
    disqualified = []
    count = 0
    base_cur = {}

    for x in cur:
        count += 1
        if count > 2:
            break

        _id = x['ts']
        pair = x['pair']
        price = x['price']
        types = x['type']
        base_cur[pair] = x['base_cur']
        
        amount = 0
        usd_value = 0

        if _id in disqualified:
            continue

        if _id not in group:
            #print('group with %s id is not found, initiate new group with id %s' % (_id, _id))
            group[_id] = {}
        try:
            orderbook = bfxclient.order_book(pair)[types]
        except:
            bfxclient = Client()
            group = {}
            break

        for o in orderbook:
            if (types == 'asks' and o['price'] <= price) or (types == 'bids' and o['price'] >= price):
                amount += o['amount']
            else:
                break

        if amount == 0:
            disqualified.append(_id)
            group.pop(_id, None)
        elif _id in group:
            usd_value = amount * price * base_cur[pair]
            group[_id][types] = "%s|%s|%s|%s" % (pair, price, amount, usd_value)
            #print("add id %s to group with type %s and amount %s" % (_id, types, amount))

    # Find min amount in each group
    min_usd_value = {}

    for _id, y in group.items():
        for types, details in y.items():
            part = details.split("|")

            pair = part[0]
            amount = float(part[2])
            usd_value = float(part[3])

            if _id not in min_usd_value or usd_value < min_usd_value[_id]:
                min_usd_value[_id] = usd_value

                if usd_value > config.max_usd_per_trade:
                    min_usd_value[_id] = config.max_usd_per_trade


    # Execute trade in each group with min amount
    amount_pair = {}
    for _id, y in group.items():
        for types, details in y.items():
            part = details.split("|")
            
            pair = part[0]
            price = float(part[1])
            amount_pair[pair] = float(min_usd_value[_id]/price*0.8)
            if 'btc' in pair.lower() or 'eth' in pair.lower():
                bc = base_cur[pair]
                amount_pair[pair] = (1/(price * bc)) * min_usd_value[_id]*0.8

            if types == "asks":
                print("SELL %s @ %s x %s" % (pair, price, amount_pair[pair]))
                bfx = TradeClient(config.key,config.secret)
                execute = bfx.place_order(amount_pair[pair], "1", "sell", "market", pair)

            elif types == "bids":
                print("BUY %s @ %s x %s" % (pair, price, amount_pair[pair]))
                bfx = TradeClient(config.key,config.secret)
                execute = bfx.place_order(amount_pair[pair], "1", "buy", "market", pair)

    
    time.sleep(1)