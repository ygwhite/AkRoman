import asyncio

from pyparsing import *
from loguru import logger


class Parser:
    def __init__(self, log):
        self.log = log

    async def parse_listing(self, lst) -> list:
        res = []
        for k, v in enumerate(lst):

            if str(v)[0].isdigit():
                try:
                    float(v)
                    is_float = True
                except ValueError:
                    is_float = False

                if is_float and k >= 1 and lst[k - 1] == ')':
                    res.append(v)
        return res

    async def parse_timeframe(self, text: str):
        time_frame_alphas = Word(alphanums)

        tf_parsing = OneOrMore('timeframe:') + time_frame_alphas
        tf_result = tf_parsing.searchString(text)
        if tf_result:
            return tf_result[0][1] if len(tf_result) >= 1 and len(tf_result[0]) == 2 else ''
        time_frame_parsing = Word(nums) + Literal('ч')
        tf_result = time_frame_parsing.searchString(text)
        if len(tf_result) > 0:
            time_interval_value = ''.join(tf_result[0])
            return time_interval_value

    async def parse_currency_pair(self, text: str):
        pair_alphas = Word(alphanums + "$/")

        pair_parsing = OneOrMore('pair:') + ZeroOrMore(' ').suppress() + pair_alphas
        pair_parsing_coin = OneOrMore('coin:') + ZeroOrMore(' ').suppress() + pair_alphas
        pair_result = pair_parsing.searchString(text) or pair_parsing_coin.searchString(text)
        if len(pair_result) >= 1:
            return pair_result[0][1] if len(pair_result[0]) == 2 else ''

        parse_exchange = Word(alphanums + ".")
        expression = Literal("тф -").suppress() + parse_exchange + Optional(Word(alphas + ';/'))
        expression_res = expression.searchString(text)
        if len(expression_res) > 0:
            expression_res = expression_res[0]
            expression_res[-1] = expression_res[-1].replace(';', '').replace('/', '')
            return ' '.join(list(expression_res))
        parse_exchange = Word(alphas + '/') + ZeroOrMore(' ') + Word(nums) + Literal('x')
        expression_res = parse_exchange.searchString(text)
        if len(expression_res) >= 1:
            exchange_value = expression_res[0][0].replace(' ', '').split('/')
            return exchange_value
        pair_parsing = OneOrMore("#") + pair_alphas
        pair_result = pair_parsing.searchString(text)
        for i in pair_result:
            return i[1]

    async def parse_signal_type(self, text):

        shorts_words = ('short', 'sell', "продажа")
        is_short = False
        longs_words = ('long', 'buy', "покупка")
        is_long = False

        for i in shorts_words:
            if is_short is False:
                is_short = text.find(i) >= 0
        for i in longs_words:
            if is_long is False:
                is_long = text.find(i) >= 0
        if is_long:
            return 'long'
        elif is_short:
            return 'short'

    async def parse_leverage(self, text):
        leverage_alphas = Word(alphanums)
        ext_symbols = Word(': ')

        leverage_parsing = OneOrMore('leverage' + ZeroOrMore(Suppress(ext_symbols))) + leverage_alphas
        leverage_result = leverage_parsing.searchString(text)

        res = leverage_result[0][1] if len(leverage_result) >= 1 and len(leverage_result[0]) == 2 else ''
        if res:
            return res
        leverage_parsing = Word(nums) + "x"
        leverage_result = leverage_parsing.searchString(text)
        if len(leverage_result) >= 1:
            leverage_value = ''.join(leverage_result[0])
            return leverage_value

    async def parse_entry_targets(self, text):
        point_parse = Word(nums)
        point_round_parse = Word(")")
        point_nums_parse = Word(nums + ".")
        entry_point = point_parse + point_round_parse + point_nums_parse + Optional('\n')

        entry_parsing = OneOrMore('entry ', ) + Optional("targets:") + Optional("zone:") + Optional('\n') + OneOrMore(
            entry_point)
        entry_result = entry_parsing.searchString(text)
        if entry_result:
            if len(entry_result) >= 1:
                return await self.parse_listing(entry_result[0])
            else:
                entry = Word(alphanums + '.,- ')
                ext_symbols = Word(': ')

                entry_parsing = (OneOrMore('entry') + ZeroOrMore(Suppress(ext_symbols)) + entry)
                entry_result = entry_parsing.searchString(text)
                if len(entry_result) >= 1:
                    return entry_result[0][1] if len(entry_result[0]) == 2 else ''
        entry_parsing = Suppress("вход:") + Word(nums + ".-") + Suppress("-") + Word(nums + ".")
        entry_result = entry_parsing.searchString(text)
        if len(entry_result) >= 1:
            entry_value = list(entry_result[0])
            return entry_value
        entry_parsing = Literal("target :") + Word(nums + " -") + Suppress("%")
        entry_result = entry_parsing.searchString(text)
        if len(entry_result) >= 1:
            entry_value = entry_result[0][-1].replace(' ', '').split('-')
            return entry_value
        entry_parsing = Literal("entry zone :") + Word(nums + " -.")
        entry_result = entry_parsing.searchString(text)
        if len(entry_result) >= 1:
            entry_value = entry_result[0][-1].replace(' ', '').split('-')
            return entry_value

    async def parse_take_profit(self, text):
        profit_parse = Word(nums)
        profit_round_parse = Word(")")
        profit_nums_parse = Word(nums + ".")
        profit = profit_parse + profit_round_parse + profit_nums_parse + Optional('\n')

        profit_parsing = OneOrMore('take-profit targets:') + Optional('\n') + OneOrMore(profit)
        profit_result = profit_parsing.searchString(text)
        if profit_result:
            if len(profit_result) >= 1:
                return await self.parse_listing(profit_result[0])
        profit_parsing = OneOrMore("tp:") + restOfLine
        tp_result = profit_parsing.searchString(text)
        if len(tp_result) >= 1:
            profit_result = tp_result[0][1].split()
            return profit_result
        entry_parsing = Literal("targets :") + Word(nums + " -.")
        entry_result = entry_parsing.searchString(text)
        if len(entry_result) >= 1:
            entry_value = entry_result[0][-1].replace(' ', '').split('-')
            return entry_value

    async def parse_stop(self, text):
        stop_parse = Word(nums)
        stop_round_parse = Word(")")
        stop_nums_parse = Word(nums + ".")
        stop = stop_parse + stop_round_parse + stop_nums_parse + Optional('\n')

        stop_parsing = OneOrMore('stop targets:') + Optional('\n') + OneOrMore(stop)
        stop_result = stop_parsing.searchString(text)
        if stop_result:
            if len(stop_result) >= 1:
                return await self.parse_listing(stop_result[0])
            else:
                entry = Word(alphanums + '.,- ')
                ext_symbols = Word(': ')

                entry_parsing = (OneOrMore('stop loss') + ZeroOrMore(Suppress(ext_symbols)) + entry)
                entry_result = entry_parsing.searchString(text)
                if len(entry_result) >= 1:
                    return entry_result[0][1] if len(entry_result[0]) == 2 else ''
        stop_parsing = OneOrMore("sl:") + restOfLine
        stop_result = stop_parsing.searchString(text)
        if len(stop_result) >= 1:
            profit_result = stop_result[0][1].split()
            return profit_result
        entry_parsing = Literal("stop loss :") + Word(nums + " -.")
        entry_result = entry_parsing.searchString(text)
        if len(entry_result) >= 1:
            entry_value = entry_result[0][-1].replace(' ', '').split('-')
            return entry_value

    async def get_price(self, text):
        price_parce = Word(nums + '.')
        price_label = Literal("цена") + Literal("=").suppress()
        expression = price_label + price_parce
        price_res = expression.searchString(text)
        if len(price_res) > 0:
            price_value = float(price_res[0][1])
            return price_value
        price_parce = Word(nums + '.') + Literal('$')
        price_res = price_parce.searchString(text)
        if len(price_res) > 0:
            price_value = float(price_res[0][0])
            return price_value

    async def parse_message(self, text):
        res = {}
        txt_low = text.lower().replace(' ', '').replace('*', '')

        # timeframe
        res['timeframe'] = await self.parse_timeframe(txt_low)

        # pairs
        res['pair'] = await self.parse_currency_pair(txt_low)
        if type(res['pair']) is list:
            res['pair'] = ''.join(res['pair'])
        # Signal type
        res['type'] = await self.parse_signal_type(txt_low)

        # Leverage
        res['leverage'] = await self.parse_leverage(txt_low)

        # Entry Targets:
        res['entry_targets'] = await self.parse_entry_targets(txt_low)
        if type(res['entry_targets']) is list and len(res['entry_targets']) > 1:
            res['entry_targets'] = res['entry_targets'][0]

        # Take Profit:
        res['take_profit'] = await self.parse_take_profit(txt_low)
        if type(res['take_profit']) is list and len(res['take_profit']) > 1:
            res['take_profit'] = res['take_profit'][0]

        # Entry Targets:
        res['stop'] = await self.parse_stop(txt_low)
        if type(res['stop']) is list and len(res['stop']) > 1:
            res['stop'] = res['stop'][0]

        # Price
        res['price'] = await self.get_price(txt_low)

        return res


#
test = Parser(logger)
# test.parse_message('hello')
work_not = """#INJ LONG 🟢
ВХОД: 7.255 - 7.111 3% от депозита
Плечо: 20x

TP: 7.335 7.440 7.647 7.993
SL:  6.986

Фиксируем:
1 тп - 25% позиции
2 тп - 50% от остатка
3 тп - 50% остатка
4 тп - 100%  позиции"""

work_not1 = """
VIP Trade ID: #R136
Pair: $SOL/USDT (Binance, ByBit)
Direction: ⬆️LONG
--------------------Target 1- $16.7Target 2- $17.1Target 3- $17.7 

(63.6% Profit - 5x lev.)🔥🔥

Booooom baby, and another one!!🚀🐋

Yours truly,
Fed. Russian Insiders®"""

work = """Timeframe: 1h
Pair: ETHUSDT
Signal type: SHORT
Leverage: 5x

Entry Targets:
 1) 1894.97

Take-Profit Targets:
 1) 1892.35
 2) 1888.43
 3) 1884.51

Stop Targets:
 1) 1917"""

testing = """❌ПРОДАЖА 1Ч ТФ - XRPUSD.P;BYBIT;Цена = 0.4894"""
test2 = """SKL/USDT 10x " Long " signal !!

Now : 0.0283$

Target : 50 - 80 - 100 - 150%

Enjoy !!"""

vip360 = """💥 Futures (New Premium Signal)

This signal was not sent by our indicators

SHORT

#HIGH/USDT

Entry zone : 1.37802-1.351000

Targets : 1.341502-1.314401-1.287300-1.260199-1.233098-1.205997-1.178896-1.151795

Stop loss :1.44557

Leverage: 5x_10x

🆔"""
x125feature = """
$BTC/USDT SHORT SCALP

⚠️HIGHRISK HEDGE SHORT TRADE!

ℹ️Expecting a rejection

Entry: 30393 - 30601 - NOW MARKET ORDER WITH LOW SIZE

SPLIT UR ENTRIES
Use 1% margin on each entry prices

HIGHER ENTRY PRICE IS BETTER AND SAFER!

TP:
1) 30068✅ June 22
2) 29778
3) 29406
4) 28698

SL: 30821 (If 1H Closing Candle ABOVE this price -1.05%)
Find us on T e l e g r a m:
@ F u t u r e s M a x L e v e r a g e

"DYOR"
#FUTURES
®️- FuturesMaxLeverage 
CLICK me to Join VIP(http://bit.ly/FML125x)

# """
# res = asyncio.run(test.parse_message(vip360))
# print(res)
