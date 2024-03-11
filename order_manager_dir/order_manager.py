import traceback
from ibapi.order import *
import os
from datetime import date


class OrderManager:
    # Class Attributes
    orderId = 1  # must be unique, as TWS API requires unique orderId's for incoming order requests, ...
    # ...gets incrementally updated (+=) with each 'use'
    def __init__(self, bot):
        try:
            self.bot = bot
            self.load_order_id()

        except Exception as e:
            print(f"Error initializing OrderManager: {e}")
            traceback.print_exc()

    def load_order_id(self):
        # Check if the file exists
        if os.path.exists("order_info.txt"):
            with open("order_info.txt", "r") as file:
                data = file.read().split()  # read the last entry in the order_id logger file
                if len(data) == 2:
                    saved_day, saved_order_id = data  # save date and order_id as a tuple
                    if saved_day == str(date.today()):
                        self.orderId = int(saved_order_id)  # return order_id as an integer
                        return
        # If file doesn't exist or the day has changed, initialize values
        self.orderId = 1
        self.save_order_id()

    def save_order_id(self):
        # Save orderId to a file
        with open("order_id.txt", "w") as file:
            file.write(f"{date.today()} {self.orderId}")  # write (or if exists, overwrite) the last order_id

    def place_order_if_entry_conditions_met(self, bar, symbol):
        try:
            print("starting order placement1")
            # if the latest rows' 'is_entry' column = 1, place an order
            #TODO remove second part of conidtional, it is just for testing + debugging
            if (self.bot.df_dict[symbol].loc[self.bot.df_dict[symbol].index[-1], 'is_entry'] == 1) or \
                    (self.bot.df_dict[symbol].loc[self.bot.df_dict[symbol].index[-1], 'Date'].minute % 2 == 0):
                print("starting order placement2")
                # Bracket Order 2% Pro fit Target 1% Stop Loss
                # Define required attributes for creating order
                #TODO check if the bar.close is in fact the right tick to use for setting the order attribut
                profitTarget = bar.close * 1.005
                stopLoss = bar.close * 0.99
                quantity = 1
                bracket = self.bracket_order(self.orderId, "BUY", quantity, profitTarget, stopLoss, symbol)
                contract = self.bot.get_symbols_contract_object(symbol)

                # Place the Bracket Order
                for order in bracket:
                    order.ocaGroup = "OCA_" + str(self.orderId)
                    order.ocaType = 2
                    # use the ib thread (used for communicating with TWS) to place orders
                    self.bot.ib.placeOrder(order.orderId, contract, order)

                #TODO this needs to tracked externally to script so it does not restart at 1 on script restart
                self.orderId += 3
                self.save_order_id()
                #TODO only have this print if the order is actually submitted
                print(f"trade entered for {symbol}")

        except Exception as e:
            print(f"Error place_order_if_entry_conditions_met: {e}")
            traceback.print_exc()

    # Bracket Order Setup
    def bracket_order(self, parentOrderID, action, quantity, profitTarget, stopLoss, symbol):
        # Create Parent Order / Initial Entry
        parent = Order()
        parent.orderId = parentOrderID
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
        print(f"order id is {profitTargetOrder.orderId}")
        profitTargetOrder.orderType = "LMT"
        profitTargetOrder.action = "SELL"
        profitTargetOrder.totalQuantity = quantity
        profitTargetOrder.lmtPrice = round(profitTarget, 2)
        profitTargetOrder.transmit = True
        profitTargetOrder.eTradeOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)
        profitTargetOrder.firmQuoteOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)

        # Stop Loss
        stopLossOrder = Order()
        stopLossOrder.orderId = parentOrderID + 2
        stopLossOrder.orderType = "STOP"
        stopLossOrder.action = "SELL"
        stopLossOrder.totalQuantity = quantity
        stopLossOrder.auxPrice = round(stopLoss, 2)
        stopLossOrder.transmit = True
        stopLossOrder.eTradeOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)
        stopLossOrder.firmQuoteOnly = ''  # API expects an empty string, as endpoint exists but is not supported (
        # weird, I know)

        bracketOrders = [parent, profitTargetOrder, stopLossOrder]

        return bracketOrders
