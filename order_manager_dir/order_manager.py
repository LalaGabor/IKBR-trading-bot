
class OrderManager:
    def __init__(self, bot):
        self.bot = bot
    def place_order_if_entry_conditions_met(self, reqID, bar, symbol):
        if self.df_dict[symbol]['is_entry'].iloc[-2] == 1:
            # Bracket Order 2% Pro fit Target 1% Stop Loss
            profitTarget = bar.close * 1.005
            stopLoss = bar.close * 0.995
            quantity = 1
            bracket = self.bracket_order(self.bot.orderId, "BUY", quantity, profitTarget, stopLoss, symbol)
            contract = self.bot.Contract()
            contract.symbol = symbol.upper()
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "EUR"

            # Place the Bracket Order
            for o in bracket:
                o.ocaGroup = "OCA_" + str(self.bot.orderId)
                o.ocaType = 2
                self.ib.placeOrder(o.orderId, contract, o)

            self.bot.orderId += 3
            print("entered order confirmed")

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