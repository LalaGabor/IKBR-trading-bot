import traceback
class OrderManager:
    # Class Attributes
    orderId = 1  # must be unique, as TWS API requires unique orderId's for incoming order requests, ...
    # ...gets incrementally updated (+=) with each 'use'
    def __init__(self, bot):
        try:
            self.bot = bot


        except Exception as e:
            print(f"Error initializing OrderManager: {e}")
            traceback.print_exc()

    def place_order_if_entry_conditions_met(self, bar, symbol):
        try:
            # if the latest rows' 'is_entry' column = 1, place an order
            #TODO remove second part of conidtional, it is just for testing + debugging
            if (self.bot.df_dict[symbol].loc[self.bot.df_dict[symbol].index[-1], 'is_entry'] == 1) and \
                    (self.bot.df_dict[symbol].loc[self.bot.df_dict[symbol].index[-1], 'Date'].minute % 5 == 0):
                # Bracket Order 2% Pro fit Target 1% Stop Loss
                # Define required attributes for creating order
                profitTarget = bar.close * 1.005
                stopLoss = bar.close * 0.99
                quantity = 1
                bracket = self.bracket_order(self.orderId, "BUY", quantity, profitTarget, stopLoss, symbol)
                contract = self.bot.get_symbols_contract_object()

                # Place the Bracket Order
                for order in bracket:
                    order.ocaGroup = "OCA_" + str(self.bot.orderId)
                    order.ocaType = 2
                    # use the ib thread (used for communicating with TWS) to place orders
                    self.bot.ib.placeOrder(order.orderId, contract, order)

                self.orderId += 3
                print(f"trade entered for {symbol}")

        except Exception as e:
            print(f"Error place_order_if_entry_conditions_met: {e}")
            traceback.print_exc()

    # Bracket Order Setup
    def bracket_order(self, parentOrderID, action, quantity, profitTarget, stopLoss, symbol):
        # Initial Entry
        # Create our IB Contract Object
        contract = self.bot.Contract()
        contract.symbol = symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "EUR"
        # Create Parent Order / Initial Entry
        parent = self.bot.Order()
        parent.orderId = parentOrderID
        parent.orderType = "MKT"
        parent.action = action
        parent.totalQuantity = quantity
        parent.transmit = False
        # Profit Target
        profitTargetOrder = self.bot.Order()
        profitTargetOrder.orderId = parentOrderID + 1
        profitTargetOrder.orderType = "LMT"
        profitTargetOrder.action = "SELL"
        profitTargetOrder.totalQuantity = quantity
        profitTargetOrder.lmtPrice = round(profitTarget, 2)
        profitTargetOrder.transmit = False
        # Stop Loss
        stopLossOrder = self.bot.Order()
        stopLossOrder.orderId = parentOrderID + 2
        stopLossOrder.orderType = "STOP"
        stopLossOrder.action = "SELL"
        stopLossOrder.totalQuantity = quantity
        stopLossOrder.auxPrice = round(stopLoss, 2)
        stopLossOrder.transmit = True

        bracketOrders = [parent, profitTargetOrder, stopLossOrder]

        return bracketOrders
