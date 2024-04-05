import traceback
from ibapi.order import *
import os
from datetime import date


class OrderManager:
    # Class Attributes
    orderId = 1  # must be unique, as TWS API requires unique orderId's for incoming order
    # requests, ...
    # ...gets incrementally updated (+=) with each 'use'
    def __init__(self, bot):
        try:
            self.bot = bot
            self.load_order_id()
        except Exception as e:
            print(f"Error initializing OrderManager: {e}")
            traceback.print_exc()

    def load_order_id(self, file_path="order_id.txt"):
        try:
            with open(file_path, "r") as file:
                data = file.read().split()  # read the last entry in the order_id logger file
                if len(data) == 2:
                    saved_day, saved_order_id = data  # save date and order_id as a tuple
                    self.orderId = int(saved_order_id)  # return order_id as an integer
                    # Learning for Sebo, a naked return, returns None. It effectively enables an early end to the
                    # function, should there be no file found
                    return
                else:
                    raise ValueError("Incorrect format in order_id.txt file.")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Order ID file '{file_path}' not found.")
        except Exception as e:
            print(f"Error loading order ID: {e}")
            raise

    def save_order_id(self):
        # Save orderId to a file
        with open("order_id.txt", "w") as file:
            file.write(f"{date.today()} {self.orderId}")  # write (or if exists, overwrite) the last order_id

    def calculate_stop_loss(self, bar_close):
        stop_loss_ratio = 0.99
        stop_loss = bar_close * stop_loss_ratio
        return stop_loss

    def calculate_profit_target(self, bar_close):
        profit_target_ratio = 1.01
        profit_target = bar_close * profit_target_ratio
        return profit_target

    def place_order_if_entry_conditions_met(self, bar, symbol):
        try:
            print("check if entry conditions met")
            # if the latest rows' 'is_entry' column = 1, place an order
            #TODO remove second part of conidtional, it is just for testing + debugging
            if (self.bot.df_dict[symbol].loc[self.bot.df_dict[symbol].index[-1], 'is_entry'] == 1) or \
                    (self.bot.df_dict[symbol].loc[self.bot.df_dict[symbol].index[-1], 'Date'].minute % 2 == 0):
                print("entry conditions met, starting order placement")
                # Define required attributes for creating order
                #TODO check if the bar.close is in fact the right tick to use for setting profit_target / stop_loss
                profit_target = self.calculate_profit_target(bar.close)
                stop_loss = self.calculate_stop_loss(bar.close)
                quantity = 1
                bracket = self.bracket_order(self.orderId, "BUY", quantity, profit_target, stop_loss, symbol)
                contract = self.bot.get_symbols_contract_object(symbol)

                # Place the Bracket Order
                for order in bracket:
                    if order == bracket[1] or order == bracket[2]:
                        order.ocaGroup = "OCA_" + str(self.orderId)
                        # print(f"order group is {order.ocaGroup}")
                        order.ocaType = 2
                        # print(f"debug order id: {order.orderId}")
                    # use the ib thread (used for communicating with TWS) to place orders                                              ""
                    self.bot.ib.placeOrder(order.orderId, contract, order)

                self.orderId += 3
                self.save_order_id()
                #TODO only have this print if the order is actually submitted
                #print(f"trade entered for {symbol}")

        except Exception as e:
            print(f"Error place_order_if_entry_conditions_met: {e}")
            traceback.print_exc()

    # Bracket Order Setup
    def bracket_order(self, parentOrderID, action, quantity, profitTarget, stopLoss, symbol):
        # Create Parent Order / Initial Entry
        parent = Order()
        parent.orderId = parentOrderID
        print(f"parent order_id is {parentOrderID}")
        parent.orderType = "MKT"
        parent.action = action
        parent.totalQuantity = quantity
        parent.transmit = True
        parent.eTradeOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)
        parent.firmQuoteOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)

        # Profit Target
        profitTargetOrder = Order()
        profitTargetOrder.orderId = parentOrderID + 1
        print(f"profitTargetOrder order_id is {profitTargetOrder.orderId}")
        profitTargetOrder.orderType = "LMT"
        profitTargetOrder.action = "SELL"
        profitTargetOrder.totalQuantity = quantity
        profitTargetOrder.lmtPrice = round(profitTarget, 2)
        print(profitTargetOrder.lmtPrice)
        profitTargetOrder.transmit = True
        profitTargetOrder.eTradeOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)
        profitTargetOrder.firmQuoteOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)

        # Stop Loss
        stopLossOrder = Order()
        stopLossOrder.orderId = parentOrderID + 2
        print(f"stopLossOrder order_id is {stopLossOrder.orderId}")
        stopLossOrder.orderType = "STOP"
        stopLossOrder.action = "SELL"
        stopLossOrder.totalQuantity = quantity
        stopLossOrder.auxPrice = round(stopLoss, 2)
        print(stopLossOrder.auxPrice)
        stopLossOrder.transmit = True
        stopLossOrder.eTradeOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)
        stopLossOrder.firmQuoteOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)

        bracketOrders = (parent, profitTargetOrder, stopLossOrder)

        return bracketOrders

