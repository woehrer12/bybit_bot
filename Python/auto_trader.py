import time
import sys
import helper.functions
import logging
import helper.bybit_api
import helper.telegramsend

logger = helper.functions.initlogger("auto_trader.log")


# TODO:
# Kompletter Telegram Bot mit Frage- Antwortfunktion


# if False:
if __name__ == "__main__":
        
    logging.info("Starting")

    while True:
    # if True:
        try:

            balance = helper.bybit_api.get_balance()

            all_positions = helper.bybit_api.get_positions()

            # closed_positions = helper.bybit_api.get_closed_positions()
            
            

            # print(all_positions)

            for position in all_positions:

                # print(position)

                current_value = float(position['markPrice']) * float(position['size'])  # Aktueller Marktwert der Position
                initial_value = float(position['avgPrice']) *float(position['size'])  # Ursprünglicher Wert der Position

                if position['side'] == 'Buy':
                    # Tatsächlicher Unrealisierter Gewinn/Verlust
                    actual_unrealised_pnl = current_value - initial_value
                    # P&L in Prozent
                    pnl_percent = round((actual_unrealised_pnl / initial_value) * 1000,2)
                    percentage_increase = round(((current_value - initial_value) / initial_value) * 100,2)
                else:
                    # Tatsächlicher Unrealisierter Gewinn/Verlust
                    actual_unrealised_pnl =  initial_value - current_value
                    # P&L in Prozent
                    pnl_percent = round((actual_unrealised_pnl / initial_value) * 1000,2)
                    percentage_increase = round(((initial_value - current_value) / initial_value) * 100,2)

                # TODO:
                # Realized P&L Tracken und wenn es zu groß wird Trade schlie0en

                

                if position['side'] == 'Buy':
                    tp2_entry = 0.15 / float(position['leverage'])
                    tp3_entry = 0.25 / float(position['leverage'])
                else:
                    tp2_entry = -0.15 / float(position['leverage'])
                    tp3_entry = -0.25 / float(position['leverage'])
                    
                tp2_entry = float(position['avgPrice']) + (float(position['avgPrice']) * tp2_entry)     
                tp3_entry = float(position['avgPrice']) + (float(position['avgPrice']) * tp3_entry)     


                # # TP 3


                if pnl_percent >= 75 and not position['stopLoss'] == '':
                    if (float(position['stopLoss']) < tp3_entry and position['side'] == 'Buy') or \
                        float(position['stopLoss']) > tp3_entry and position['side'] == 'Sell':

                        print(balance['totalAvailableBalance'] + " USDT ")

                        text =  "Symbol: " + position['symbol'] + " " + position['leverage'] + " " + position['avgPrice'] + "\n" + \
                        "Market: " + position['markPrice'] + " " + position['size'] + "\n" + \
                        "P&L: " + str(pnl_percent) + '%' + "\n" + \
                        "Side: " + position['side'] + "\n" + \
                        "Price: " + str(percentage_increase) + '%' + "\n" + \
                        "SL: " + position['stopLoss']

                        print(position['symbol'] + ' ' + position['leverage'] + ' ' + position['avgPrice'])
                        print(position['markPrice'] + ' ' + position['size'])
                        print(position['side'])
                        print("P&L: ", pnl_percent, '%')
                        print("Price: ", percentage_increase, '%')
                        print("SL: ", position['stopLoss'])

                        print()

                        print('TP3 !!')
                        text = text + "\n" + "TP3!!"
                        
                        # TODO Test it with Short

                        infos = helper.bybit_api.get_instruments_info(position['symbol'])
                        
                        if position['side'] == 'Buy':
                            sl_factor = 0.5 / float(position['leverage'])
                            sl_tp3_factor = 0.7 / float(position['leverage'])
                            price6 = 0.6 / float(position['leverage'])

                        else:
                            sl_factor = -0.5 / float(position['leverage'])
                            sl_tp3_factor = -0.7 / float(position['leverage'])
                            price6 = -0.6 / float(position['leverage'])


                        sl_price = float(position['avgPrice']) + (float(position['avgPrice']) * sl_factor)
                        tp3_price = float(position['avgPrice']) + (float(position['avgPrice']) * sl_tp3_factor)
                        tp3_size = float(position['size']) * 0.5
                        price6 = float(position['avgPrice']) - (float(position['avgPrice']) * price6)
                        qty6 = float(position['size']) * 0.5


                        price6 = helper.bybit_api.round_ticksize(price6, infos['priceFilter']['tickSize'])
                        qty6 = helper.bybit_api.round_ticksize(qty6, infos['lotSizeFilter']['qtyStep'])
                        sl_price = helper.bybit_api.round_ticksize(sl_price, infos['priceFilter']['tickSize'])
                        tp3_price = helper.bybit_api.round_ticksize(tp3_price, infos['priceFilter']['tickSize'])
                        tp3_size = helper.bybit_api.round_ticksize(tp3_size, infos['lotSizeFilter']['qtyStep'])

                        print("SL: ", sl_price)
                        text = text + "\n" + "SL: " + str(sl_price)

                        print("TP: ", tp3_price)
                        text = text + "\n" + "TP3: " + str(tp3_price) + "Size: " + str(tp3_size)

                        print("Order6 : " + str(price6) + " Size: " + str(qty6))
                        text = text + "\n" + "Order6 : " + str(price6) + " Size: " + str(qty6)


                        helper.bybit_api.cancel_all_orders_symbol(position['symbol'])
                        helper.bybit_api.cancel_all_stop_orders_symbol(position['symbol'])
                        helper.bybit_api.set_sl(position['symbol'], sl_price)
                        helper.bybit_api.set_part_sl(position['symbol'], tp3_price, tp3_size)
                        # helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price6, qty6)


                        helper.telegramsend.send(text)

                        logging.info(text)


                # # TP 2           

                if pnl_percent >= 35 and pnl_percent < 55 and not position['stopLoss'] == '':
                    if (float(position['stopLoss']) < tp2_entry and position['side'] == 'Buy') or \
                        float(position['stopLoss']) > tp2_entry and position['side'] == 'Sell':

                        print(balance['totalAvailableBalance'] + " USDT ")

                        text =  "Symbol: " + position['symbol'] + " " + position['leverage'] + " " + position['avgPrice'] + "\n" + \
                        "Market: " + position['markPrice'] + " " + position['size'] + "\n" + \
                        "P&L: " + str(pnl_percent) + '%' + "\n" + \
                        "Side: " + position['side'] + "\n" + \
                        "Price: " + str(percentage_increase) + '%' + "\n" + \
                        "SL: " + position['stopLoss']

                        print(position['symbol'] + ' ' + position['leverage'] + ' ' + position['avgPrice'])
                        print(position['markPrice'] + ' ' + position['size'])
                        print(position['side'])
                        print("P&L: ", pnl_percent, '%')
                        print("Price: ", percentage_increase, '%')
                        print("SL: ", position['stopLoss'])

                        print()

                        print('TP2 !!')
                        text = text + "\n" + "TP2!!"
                        
                        # TODO Test it with Short

                        infos = helper.bybit_api.get_instruments_info(position['symbol'])
                        
                        if position['side'] == 'Buy':
                            sl_factor = 0.2 / float(position['leverage'])
                            sl_tp2_factor = 0.25 / float(position['leverage'])
                            price5 = 0.3 / float(position['leverage'])
                            pricetp1 = 0.45 / float(position['leverage'])
                            pricetp2 = 0.5 / float(position['leverage'])
                            pricetp3 = 0.55 / float(position['leverage'])

                        else:
                            sl_factor = -0.2 / float(position['leverage'])
                            sl_tp2_factor = -0.25 / float(position['leverage'])
                            price5 = -0.3 / float(position['leverage'])
                            pricetp1 = -0.45 / float(position['leverage'])
                            pricetp2 = -0.5 / float(position['leverage'])
                            pricetp3 = -0.55 / float(position['leverage'])


                        sl_price = float(position['avgPrice']) + (float(position['avgPrice']) * sl_factor)
                        tp2_price = float(position['avgPrice']) + (float(position['avgPrice']) * sl_tp2_factor)
                        tp2_size = float(position['size']) * 0.5
                        price5 = float(position['avgPrice']) - (float(position['avgPrice']) * price5)
                        qty5 = float(position['size']) * 0.5


                        price5 = helper.bybit_api.round_ticksize(price5, infos['priceFilter']['tickSize'])
                        qty5 = helper.bybit_api.round_ticksize(qty5, infos['lotSizeFilter']['qtyStep'])
                        qtytp1 = float(position['size']) * 0.1
                        qtytp2 = float(position['size']) * 0.1
                        qtytp3 = float(position['size']) * 0.1
                        sl_price = float(position['avgPrice']) + (float(position['avgPrice']) * sl_factor)
                        pricetp1 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp1)
                        pricetp2 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp2)
                        pricetp3 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp3)
                        tp2_price = helper.bybit_api.round_ticksize(tp2_price, infos['priceFilter']['tickSize'])
                        tp2_size = helper.bybit_api.round_ticksize(tp2_size, infos['lotSizeFilter']['qtyStep'])
                        qtytp1 = helper.bybit_api.round_ticksize(qtytp1, infos['lotSizeFilter']['qtyStep'])
                        qtytp2 = helper.bybit_api.round_ticksize(qtytp2, infos['lotSizeFilter']['qtyStep'])
                        qtytp3 = helper.bybit_api.round_ticksize(qtytp3, infos['lotSizeFilter']['qtyStep'])
                        pricetp1 = helper.bybit_api.round_ticksize(pricetp1, infos['priceFilter']['tickSize'])
                        pricetp2 = helper.bybit_api.round_ticksize(pricetp2, infos['priceFilter']['tickSize'])
                        pricetp3 = helper.bybit_api.round_ticksize(pricetp3, infos['priceFilter']['tickSize'])



                        print("SL: ", sl_price)
                        text = text + "\n" + "SL: " + str(sl_price)

                        print("TP: ", tp2_price)
                        text = text + "\n" + "TP2: " + str(tp2_price) + "Size: " + str(tp2_size)

                        print("Order5 : " + str(price5) + " Size: " + str(qty5))
                        text = text + "\n" + "Order5 : " + str(price5) + " Size: " + str(qty5)

                        print("TP1 : " + str(pricetp1) + " Size: " + str(qtytp1))
                        print("TP2 : " + str(pricetp2) + " Size: " + str(qtytp2))
                        print("TP3 : " + str(pricetp3) + " Size: " + str(qtytp3))
                        text = text + "\n" + "TP1 : " + str(pricetp1) + " Size: " + str(qtytp1)
                        text = text + "\n" + "TP2 : " + str(pricetp2) + " Size: " + str(qtytp2)
                        text = text + "\n" + "TP3 : " + str(pricetp3) + " Size: " + str(qtytp3)

                        helper.bybit_api.cancel_all_orders_symbol(position['symbol'])
                        helper.bybit_api.cancel_all_stop_orders_symbol(position['symbol'])
                        helper.bybit_api.set_sl(position['symbol'], sl_price)
                        helper.bybit_api.set_part_sl(position['symbol'], tp2_price, tp2_size)
                        # helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price5, qty5)
                        helper.bybit_api.set_part_tp(position['symbol'], pricetp1, qtytp1)
                        helper.bybit_api.set_part_tp(position['symbol'], pricetp2, qtytp2)
                        helper.bybit_api.set_part_tp(position['symbol'], pricetp3, qtytp3)



                        helper.telegramsend.send(text)

                        logging.info(text)


                # TP 1
                if pnl_percent >= 15 and pnl_percent < 35 and not position['stopLoss'] == '':
                    if (float(position['stopLoss']) < float(position['avgPrice']) and position['side'] == 'Buy') or \
                        float(position['stopLoss']) > float(position['avgPrice']) and position['side'] == 'Sell':

                        print(balance['totalAvailableBalance'] + " USDT ")

                        text =  "Symbol: " + position['symbol'] + " " + position['leverage'] + " " + position['avgPrice'] + "\n" + \
                        "Market: " + position['markPrice'] + " " + position['size'] + "\n" + \
                        "Side: " + position['side'] + "\n" + \
                        "P&L: " + str(pnl_percent) + '%' + "\n" + \
                        "Price: " + str(percentage_increase) + '%' + "\n" + \
                        "SL: " + position['stopLoss']

                        print(position['symbol'] + ' ' + position['leverage'] + ' ' + position['avgPrice'])
                        print(position['markPrice'] + ' ' + position['size'])
                        print(position['side'])
                        print("P&L: ", pnl_percent, '%')
                        print("Price: ", percentage_increase, '%')
                        print("SL: ", position['stopLoss'])

                        print()

                        print('TP1 !!')
                        text = text + "\n" + "TP1!!"

                        infos = helper.bybit_api.get_instruments_info(position['symbol'])

                        if position['side'] == 'Buy':
                            sl_factor = 0.05 / float(position['leverage'])
                            sl_tp1_factor = 0.1 / float(position['leverage'])
                            price4 = 0.125 / float(position['leverage'])
                            pricetp1 = 0.25 / float(position['leverage'])
                            pricetp2 = 0.3 / float(position['leverage'])
                            pricetp3 = 0.35 / float(position['leverage'])

                        else:
                            sl_factor = -0.05 / float(position['leverage'])
                            sl_tp1_factor = -0.1 / float(position['leverage'])
                            price4 = -0.125 / float(position['leverage'])
                            pricetp1 = -0.25 / float(position['leverage'])
                            pricetp2 = -0.3 / float(position['leverage'])
                            pricetp3 = -0.35 / float(position['leverage'])


                        qtytp1 = float(position['size']) * 0.1
                        qtytp2 = float(position['size']) * 0.1
                        qtytp3 = float(position['size']) * 0.1
                        sl_price = float(position['avgPrice']) + (float(position['avgPrice']) * sl_factor)
                        pricetp1 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp1)
                        pricetp2 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp2)
                        pricetp3 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp3)
                        tp1_price = float(position['avgPrice']) + (float(position['avgPrice']) * sl_tp1_factor)
                        price4 = float(position['avgPrice']) + (float(position['avgPrice']) * price4)
                        qty4 = float(position['size']) * 0.2
                        tp1_size = float(position['size']) * 0.3

                        sl_price = helper.bybit_api.round_ticksize(sl_price, infos['priceFilter']['tickSize'])
                        tp1_price = helper.bybit_api.round_ticksize(tp1_price, infos['priceFilter']['tickSize'])
                        tp1_size = helper.bybit_api.round_ticksize(tp1_size, infos['lotSizeFilter']['qtyStep'])
                        price4 = helper.bybit_api.round_ticksize(price4, infos['priceFilter']['tickSize'])
                        qty4 = helper.bybit_api.round_ticksize(qty4, infos['lotSizeFilter']['qtyStep'])
                        qtytp1 = helper.bybit_api.round_ticksize(qtytp1, infos['lotSizeFilter']['qtyStep'])
                        qtytp2 = helper.bybit_api.round_ticksize(qtytp2, infos['lotSizeFilter']['qtyStep'])
                        qtytp3 = helper.bybit_api.round_ticksize(qtytp3, infos['lotSizeFilter']['qtyStep'])
                        pricetp1 = helper.bybit_api.round_ticksize(pricetp1, infos['priceFilter']['tickSize'])
                        pricetp2 = helper.bybit_api.round_ticksize(pricetp2, infos['priceFilter']['tickSize'])
                        pricetp3 = helper.bybit_api.round_ticksize(pricetp3, infos['priceFilter']['tickSize'])


                        print("SL: ", sl_price)
                        text = text + "\n" + "SL: " + str(sl_price)

                        print("TP: ", tp1_price)
                        text = text + "\n" + "TP1: " + str(tp1_price) + "Size: " + str(tp1_size)

                        print("Order4 : " + str(price4) + " Size: " + str(qty4))
                        text = text + "\n" + "Order4 : " + str(price4) + " Size: " + str(qty4)

                        print("TP1 : " + str(pricetp1) + " Size: " + str(qtytp1))
                        print("TP2 : " + str(pricetp2) + " Size: " + str(qtytp2))
                        print("TP3 : " + str(pricetp3) + " Size: " + str(qtytp3))
                        text = text + "\n" + "TP1 : " + str(pricetp1) + " Size: " + str(qtytp1)
                        text = text + "\n" + "TP2 : " + str(pricetp2) + " Size: " + str(qtytp2)
                        text = text + "\n" + "TP3 : " + str(pricetp3) + " Size: " + str(qtytp3)


                        helper.bybit_api.cancel_all_stop_orders_symbol(position['symbol'])
                        helper.bybit_api.cancel_all_orders_symbol(position['symbol'])
                        helper.bybit_api.set_sl(position['symbol'], sl_price)
                        helper.bybit_api.set_part_sl(position['symbol'], tp1_price, tp1_size)
                        # helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price4, qty4)

                        
                        helper.bybit_api.set_part_tp(position['symbol'], pricetp1, qtytp1)
                        helper.bybit_api.set_part_tp(position['symbol'], pricetp2, qtytp2)
                        helper.bybit_api.set_part_tp(position['symbol'], pricetp3, qtytp3)

                        helper.telegramsend.send(text)

                        logging.info(text)


                # SL

                if position['stopLoss'] == '':
                    
                    text =  "Symbol: " + position['symbol'] + " " + position['leverage'] + " " + position['avgPrice'] + "\n" + \
                            "Market: " + position['markPrice'] + " " + position['size'] + "\n" + \
                            "Side: " + position['side'] + "\n" + \
                            "P&L: " + str(pnl_percent) + '%' + "\n" + \
                            "Price: " + str(percentage_increase) + '%' + "\n" + \
                            "SL: " + position['stopLoss']

                    print(balance['totalAvailableBalance'] + " USDT ")

                    print(position['symbol'] + ' ' + position['leverage'] + ' ' + position['avgPrice'])
                    print(position['markPrice'] + ' ' + position['size'])
                    print(position['side'])
                    print("P&L: ", pnl_percent, '%')
                    print("Price: ", percentage_increase, '%')
                    print("SL: ", position['stopLoss'])

                    print()

                    print("Initial StopLoss")

                    text = text + "\n" + "Inital StopLoss"

                    print(position['side'])

                    infos = helper.bybit_api.get_instruments_info(position['symbol'])

                    if position['side'] == 'Buy':
                        sl_factor = 0.35 / float(position['leverage'])
                        price1 = 0.05 / float(position['leverage'])
                        price2 = 0.1 / float(position['leverage'])
                        price3 = 0.15 / float(position['leverage'])
                        price4 = 0.2 / float(position['leverage'])
                        price5 = 0.25 / float(position['leverage'])
                        price6 = 0.3 / float(position['leverage'])
                        pricetp1 = 0.05 / float(position['leverage'])
                        pricetp2 = 0.1 / float(position['leverage'])
                        pricetp3 = 0.15 / float(position['leverage'])

                    else:
                        sl_factor = -0.35 / float(position['leverage'])
                        price1 = -0.05 / float(position['leverage'])
                        price2 = -0.1 / float(position['leverage'])
                        price3 = -0.15 / float(position['leverage'])
                        price4 = -0.2 / float(position['leverage'])
                        price5 = -0.25 / float(position['leverage'])
                        price6 = -0.3 / float(position['leverage'])
                        pricetp1 = -0.05 / float(position['leverage'])
                        pricetp2 = -0.1 / float(position['leverage'])
                        pricetp3 = -0.15 / float(position['leverage'])
                    


                    price1 = float(position['avgPrice']) - (float(position['avgPrice']) * price1)
                    price2 = float(position['avgPrice']) - (float(position['avgPrice']) * price2)
                    price3 = float(position['avgPrice']) - (float(position['avgPrice']) * price3)
                    price4 = float(position['avgPrice']) - (float(position['avgPrice']) * price4)
                    price5 = float(position['avgPrice']) - (float(position['avgPrice']) * price5)
                    price6 = float(position['avgPrice']) - (float(position['avgPrice']) * price6)
                    qty1 = float(position['size']) * 0.25
                    qty2 = float(position['size']) * 0.5
                    qty3 = float(position['size']) * 0.75
                    qty4 = float(position['size']) * 1
                    qty5 = float(position['size']) * 1.5
                    qty6 = float(position['size']) * 2
                    qtytp1 = float(position['size']) * 0.1
                    qtytp2 = float(position['size']) * 0.1
                    qtytp3 = float(position['size']) * 0.1
                    sl_price = float(position['avgPrice']) - (float(position['avgPrice']) * sl_factor)
                    pricetp1 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp1)
                    pricetp2 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp2)
                    pricetp3 = float(position['avgPrice']) + (float(position['avgPrice']) * pricetp3)

                    price1 = helper.bybit_api.round_ticksize(price1, infos['priceFilter']['tickSize'])
                    price2 = helper.bybit_api.round_ticksize(price2, infos['priceFilter']['tickSize'])
                    price3 = helper.bybit_api.round_ticksize(price3, infos['priceFilter']['tickSize'])
                    price4 = helper.bybit_api.round_ticksize(price4, infos['priceFilter']['tickSize'])
                    price5 = helper.bybit_api.round_ticksize(price5, infos['priceFilter']['tickSize'])
                    price6 = helper.bybit_api.round_ticksize(price6, infos['priceFilter']['tickSize'])
                    qty1 = helper.bybit_api.round_ticksize(qty1, infos['lotSizeFilter']['qtyStep'])
                    qty2 = helper.bybit_api.round_ticksize(qty2, infos['lotSizeFilter']['qtyStep'])
                    qty3 = helper.bybit_api.round_ticksize(qty3, infos['lotSizeFilter']['qtyStep'])
                    qty4 = helper.bybit_api.round_ticksize(qty4, infos['lotSizeFilter']['qtyStep'])
                    qty5 = helper.bybit_api.round_ticksize(qty5, infos['lotSizeFilter']['qtyStep'])
                    qty6 = helper.bybit_api.round_ticksize(qty6, infos['lotSizeFilter']['qtyStep'])
                    qtytp1 = helper.bybit_api.round_ticksize(qtytp1, infos['lotSizeFilter']['qtyStep'])
                    qtytp2 = helper.bybit_api.round_ticksize(qtytp2, infos['lotSizeFilter']['qtyStep'])
                    qtytp3 = helper.bybit_api.round_ticksize(qtytp3, infos['lotSizeFilter']['qtyStep'])
                    sl_price = helper.bybit_api.round_ticksize(sl_price, infos['priceFilter']['tickSize'])
                    pricetp1 = helper.bybit_api.round_ticksize(pricetp1, infos['priceFilter']['tickSize'])
                    pricetp2 = helper.bybit_api.round_ticksize(pricetp2, infos['priceFilter']['tickSize'])
                    pricetp3 = helper.bybit_api.round_ticksize(pricetp3, infos['priceFilter']['tickSize'])

                    print("SL: ", sl_price)
                    text = text + "\n" + "SL: " + str(sl_price)

                    print("Order1 : " + str(price1) + " Size: " + str(qty1))
                    print("Order2 : " + str(price2) + " Size: " + str(qty2))
                    print("Order3 : " + str(price3) + " Size: " + str(qty3))
                    print("Order4 : " + str(price4) + " Size: " + str(qty4))
                    print("Order5 : " + str(price5) + " Size: " + str(qty5))
                    print("Order6 : " + str(price6) + " Size: " + str(qty6))
                    text = text + "\n" + "Order1 : " + str(price1) + " Size: " + str(qty1)
                    text = text + "\n" + "Order2 : " + str(price2) + " Size: " + str(qty2)
                    text = text + "\n" + "Order3 : " + str(price3) + " Size: " + str(qty3)
                    text = text + "\n" + "Order4 : " + str(price4) + " Size: " + str(qty4)
                    text = text + "\n" + "Order5 : " + str(price5) + " Size: " + str(qty5)
                    text = text + "\n" + "Order6 : " + str(price6) + " Size: " + str(qty6)

                    print("TP1 : " + str(pricetp1) + " Size: " + str(qtytp1))
                    print("TP2 : " + str(pricetp2) + " Size: " + str(qtytp2))
                    print("TP3 : " + str(pricetp3) + " Size: " + str(qtytp3))
                    text = text + "\n" + "TP1 : " + str(pricetp1) + " Size: " + str(qtytp1)
                    text = text + "\n" + "TP2 : " + str(pricetp2) + " Size: " + str(qtytp2)
                    text = text + "\n" + "TP3 : " + str(pricetp3) + " Size: " + str(qtytp3)


                    helper.bybit_api.cancel_all_stop_orders_symbol(position['symbol'])
                    helper.bybit_api.cancel_all_orders_symbol(position['symbol'])

                    helper.bybit_api.set_sl(position['symbol'], sl_price)

                    helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price1, qty1)
                    helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price2, qty2)
                    helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price3, qty3)
                    helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price4, qty4)
                    helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price5, qty5)
                    helper.bybit_api.place_order(position['symbol'], position['side'], "Limit", price6, qty6)

                    helper.bybit_api.set_part_tp(position['symbol'], pricetp1, qtytp1)
                    helper.bybit_api.set_part_tp(position['symbol'], pricetp2, qtytp2)
                    helper.bybit_api.set_part_tp(position['symbol'], pricetp3, qtytp3)

                    helper.telegramsend.send(text)

                    logging.info(text)


            time.sleep(1)

        except Exception as e:
            print("Error while Auto Trader:" + \
                str(sys.exc_info()) + "\n" + \
                str(e.args))
            logging.error("Error while Auto Trader" + str(sys.exc_info()) + \
                str(sys.exc_info()) + "\n" + \
                str(e.args))


    