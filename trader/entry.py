from pymongo import MongoClient
from client import TradeClient, Client
import time
#import config

#bfx = TradeClient(config.key,config.secret)
#execute = bfx.place_order("10", "1", "buy", "market", "iotusd")


bfxclient = Client()

order = MongoClient().wtracker.orders
lookback = 1


def price_in_usd(pair, amount, rate):
    return 1

while(1):

    t = int(time.time())-lookback
    cur = order.find( { 'ts' : { '$gt' : t } } )
    order.delete_many( { 'ts' : { '$lt' : t-lookback } } )

    # look for most expensive in ASKS
    # look for cheapest in BIDS
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
            print("orderbook timed out")
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
    min_amount = {}

    for _id, y in group.items():
        for types, details in y.items():
            part = details.split("|")

            pair = part[0]
            amount = float(part[2])
            usd_value = float(part[3])

            if _id not in min_usd_value or usd_value < min_usd_value[_id]:
                min_usd_value[_id] = usd_value
                min_amount[_id] = amount


    # Execute trade in each group with min amount
    amount_pair = {}
    for _id, y in group.items():
        for types, details in y.items():
            part = details.split("|")
            
            pair = part[0]
            price = float(part[1])
            amount_pair[pair] = float(part[2])
            if 'btc' in pair.lower() or 'eth' in pair.lower():
                bc = base_cur[pair]
                amount_pair[pair] = (1/(price * bc)) * min_usd_value[_id]*0.75

            if types == "asks":
                print("SELL %s @ %s x %s" % (pair, price, amount_pair[pair]))

            elif types == "bids":
                print("BUY %s @ %s x %s" % (pair, price, amount_pair[pair]))
    try:
        time.sleep(1)
    except:
        print("unknowned KeyboardInterrupt error on time.sleep")
