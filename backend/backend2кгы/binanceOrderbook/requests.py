
from decimal import Decimal
import pandas as pd
import requests
import math
from loguru._logger import Logger



class BinanceOrderbook:
    __slots__ = "log", "url"

    def __init__(self,
                 baseurl: str,
                 log: Logger,
                 ):

        self.url = baseurl
        self.log = log

    # {'lastUpdateId': 30500241610, 'E': 1678894478990, 'T': 1678894478987,
    #  'bids': [['24558.90', '64.251'], ['24539.60', '51.497'], ['24536.30', '118.111'], ['24528.50', '0.001'],
    #           ['24525.00', '19.620'], ['24524.40', '3.058'], ['24518.10', '0.020'], ['24518.00', '0.040'],
    #           ['24513.80', '3.582'], ['24511.10', '8.917']],
    #  'asks': [['24564.30', '32.674'], ['24568.60', '0.447'], ['24570.60', '48.573'], ['24600.50', '0.001'],
    #           ['24601.10', '21.819'], ['24608.00', '28.572'], ['24622.70', '59.968'], ['24623.60', '0.001'],
    #           ['24625.60', '10.505'], ['24647.10', '189.650']]}
    def table_styling(self, df, side):
        if side == "ask":
            bar_color = "rgba(230,31,7,0.2)"
            font_color = "rgb(230,31,7)"
        elif side == "bid":
            bar_color = "rgb(13,230,49,0.2)"
            font_color = "rgb(13,230,49)"
        cell_bg_color = "#060606"
        styles = []

        styles.append({
            "if": {"column_id": "price"},
            "color": font_color,
            "background-color": cell_bg_color,
        })

        return styles

    def aggregate_levels(self, levels_df, agg_level=Decimal('1'), side="bid"):
        if side == "bid":
            right = False
            label_func = lambda x: x.left
        else:
            right = True;
            label_func = lambda x: x.right

        min_level = math.floor(Decimal(min(levels_df.price)) / agg_level - 1) * agg_level
        max_level = math.ceil(Decimal(max(levels_df.price)) / agg_level + 1) * agg_level

        level_bounds = [float(min_level + agg_level * x) for x in range(int((max_level - min_level) / agg_level) + 1)]

        levels_df["bin"] = pd.cut(levels_df.price, bins=level_bounds, precision=10, right=right)

        levels_df = levels_df.groupby("bin").agg(quantity=("quantity", "sum")).reset_index()

        levels_df["price"] = levels_df.bin.apply(label_func)
        levels_df = levels_df[levels_df.quantity > 0]
        levels_df = levels_df[["price", "quantity"]]

        return levels_df

    def update_orderbook(self, agg_level, quantity_precision, price_precision, symbol):
        url = self.url

        levels_to_show = 10

        params = {
            "symbol": symbol.upper(),
            "limit": 1000,
        }

        data = requests.get(url, params=params).json()

        # ["0.01", "0.1", "1", "10", "100"],
        any_price_val = float(data ['bids'][400][0])

        if any_price_val >= 1000:
            agg_level = 100
            quantity_precision = 0
            price_precision = 0
        elif 1000 > any_price_val > 100:
            agg_level = 10
            quantity_precision = 0
            price_precision = 1
        elif 100 > any_price_val > 10:
            agg_level = 10
            quantity_precision = 1
            price_precision = 2
        elif 10 > any_price_val > 1:
            agg_level = 1
            quantity_precision = 2
            price_precision = 3
        elif 1 > any_price_val > 0.1:
            agg_level = 0.1
            quantity_precision = 3
            price_precision = 4
        elif 0.1 > any_price_val:
            agg_level = 0.01
            quantity_precision = 4
            price_precision = 4
        bid_df = pd.DataFrame(data["bids"], columns=["price", "quantity"], dtype=float)
        ask_df = pd.DataFrame(data["asks"], columns=["price", "quantity"], dtype=float)

        bid_df = self.aggregate_levels(bid_df, agg_level=Decimal(agg_level), side="bid")
        bid_df = bid_df.sort_values("price", ascending=False)

        ask_df = self.aggregate_levels(ask_df, agg_level=Decimal(agg_level), side="ask")
        ask_df = ask_df.sort_values("price", ascending=False)

        mid_price = (bid_df.price.iloc[0] + ask_df.price.iloc[-1]) / 2
        mid_price = f"%.{quantity_precision}f" % mid_price

        bid_df = bid_df.iloc[:levels_to_show]
        ask_df = ask_df.iloc[-levels_to_show:]

        bid_df.quantity = bid_df.quantity.apply(
            lambda x: f"%.{quantity_precision}f" % x)

        ask_df.quantity = ask_df.quantity.apply(
            lambda x: f"%.{quantity_precision}f" % x)

        bid_df.price = bid_df.price.apply(
            lambda x: f"%.{price_precision}f" % x)

        ask_df.price = ask_df.price.apply(
            lambda x: f"%.{price_precision}f" % x)

        return (bid_df.to_dict("records"),
                ask_df.to_dict("records"), mid_price)

    async def lst_ob_to_text(self, lst, sep):
        res = ''
        for i in lst:
            price = i['price']
            qty = i['quantity']
            res += f'{sep}{price} : <b>{qty}</b>\n'
        return res

    async def get_orderbook_text(self, symbol):
        try:
            # Aggregate Level options=["0.01", "0.1", "1", "10", "100"],
            # Quantity Precision options=["0", "1", "2", "3", "4"],
            # Price Precision options = ["0", "1", "2", "3", "4"],
            order_book = self.update_orderbook(10, 0, 1, symbol)
            asks_text = await self.lst_ob_to_text(order_book[1], sep="🟩")
            bids_text = await self.lst_ob_to_text(order_book[0], sep="🟥")

        except Exception as e:
            self.log.exception(e)
            return ''
        return bids_text + asks_text
