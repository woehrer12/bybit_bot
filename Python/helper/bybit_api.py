import helper.config
import math

import sys
import logging

from pybit.unified_trading import HTTP

conf = helper.config.initconfig()

api_key = conf['bybit_api_key']
api_secret = conf['bybit_api_secret']


def round_ticksize(zahl, teilbarkeit):
    zahl = float(zahl)
    teilbarkeit = float(teilbarkeit)
    return math.ceil(zahl / teilbarkeit) * teilbarkeit

# def round_ticksize(zahl, teilbarkeit):
#     zahl = float(zahl)
#     teilbarkeit = float(teilbarkeit)
#     return round(zahl / teilbarkeit) * teilbarkeit


def get_balance():
    
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    try:
        return session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]
    except Exception as e:
        print("Error while get balance:" + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        logging.error("Error while get balance:" + str(sys.exc_info()) + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        

def get_positions():
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    try:
        return session.get_positions(category="linear", settleCoin = "USDT")['result']['list']
    except Exception as e:
        print("Error while get positions:" + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        logging.error("Error while get positions:" + str(sys.exc_info()) + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))

def set_sl(symbol, price):
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    try:
        result = session.set_trading_stop(
                                            category="linear", 
                                            symbol = symbol, 
                                            stopLoss = str(price),
                                            positionIdx = 0,
                                        )
        print(result)
    except Exception as e:
        print("Error while set SL:" + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        logging.error("Error while set SL" + str(sys.exc_info()) + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))

def set_part_sl(symbol, price, size):
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    try:
        result = session.set_trading_stop(  
                                            category="linear",
                                            symbol=symbol,
                                            takeProfit="0",
                                            stopLoss=price,
                                            tpTriggerBy="MarkPrice",
                                            slTriggerB="MarkPrice",
                                            tpslMode="Partial",
                                            tpOrderType="Market",
                                            slOrderType="Limit",
                                            tpSize="0",
                                            slSize=str(size),
                                            tpLimitPrice="0",
                                            slLimitPrice=str(price),
                                            positionIdx=0,
                                            )
        print(result)

    except Exception as e:
        print("Error while set Part SL:" + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        logging.error("Error while set Part SL:" + str(sys.exc_info()) + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        
def set_part_tp(symbol, price, size):
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    try:
        result = session.set_trading_stop(  
                                            category="linear",
                                            symbol=symbol,
                                            takeProfit=price,
                                            stopLoss="0",
                                            tpTriggerBy="MarkPrice",
                                            slTriggerB="MarkPrice",
                                            tpslMode="Partial",
                                            tpOrderType="Limit",
                                            slOrderType="Market",
                                            tpSize=str(size),
                                            slSize="0",
                                            tpLimitPrice=str(price),
                                            slLimitPrice="0",
                                            positionIdx=0,
                                            )
        print(result)

    except Exception as e:
        print("Error while set Part TP:" + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        logging.error("Error while set Part TP:" + str(sys.exc_info()) + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))


def place_order(symbol, side, orderType, price, qty):
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    try:
        result = session.place_order(category="linear", symbol = symbol, side =side, orderType = orderType, price = price, qty =qty)
        print(result)
    except Exception as e:
        print("Error while place Order:" + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        logging.error("Error while place Order" + str(sys.exc_info()) + \
            str(sys.exc_info()) + "\n" + \
            str(e.args))
        
def get_instruments_info(symbol):
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    result = session.get_instruments_info(category="linear", symbol = symbol)['result']['list'][0]
    return result

def cancel_all_orders_symbol(symbol):
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    result = session.cancel_all_orders(category="linear",symbol = symbol, orderFilter = "Order")
    print(result)

def cancel_all_stop_orders_symbol(symbol):
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    result = session.cancel_all_orders(category="linear",symbol = symbol, orderFilter = "StopOrder")
    print(result)

def get_closed_positions():
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
    result = session.get_closed_pnl(category="linear")['result']['list']

    for results in result:
        print(results)

    return None