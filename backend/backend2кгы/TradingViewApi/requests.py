import json

from loguru._logger import Logger

from utils.requests import BaseRequest


class TradingViewApi:
    __slots__ = "log", "rh", "url", "indicatorIds_dict", 'sessionId', 'sessionSign'

    def __init__(self,
                 baseurl: str,
                 request_handler: BaseRequest,
                 log: Logger, indicatorIds_dict: dict, sessionId: str, sessionSign: str
                 ):

        self.url = baseurl
        self.rh = request_handler
        self.log = log
        self.indicatorIds_dict = indicatorIds_dict
        self.sessionId = sessionId
        self.sessionSign = sessionSign

    async def send_req(self, sessionId, sessionSign, range, timeframe, currency, indicatorId) -> str:
        try:
            # TRADING_VIEW_API_URL = "http://localhost:80/get-indicator-graphic?sessionId={sessionId}&range={range}&timeframe={timeframe}&currency={currency}&indicatorId={indicatorId}"
            response = await self.rh.request("get",
                                             self.url.format(sessionId=sessionId, sessionSign=sessionSign, range=range,
                                                             timeframe=timeframe,
                                                             currency=currency, indicatorId=indicatorId))
            content_json = response.content
            content_lst = json.loads(content_json)
            return content_lst
        except Exception as e:
            self.log.exception(e)
            return None

    async def _get_bids_ack_lst(self, symbol):
        res_json = await self.send_req(symbol)
        res = {}
        return res

    async def lst_to_text(self, lst, sep):
        res = ''
        return res

    async def test_is_case(self, currency, tf, res):
        # here test all indicators

        # RSI 1
        if tf == "5" and res.get("RSI", None)[0].get("RSI", None):
            return True

        if res["Market Cipher B"]:
            if True:
                return True
        elif res["VuManChu Cipher B"]:
            if True:
                return True
        elif res["RSI"]:
            if True:
                return True
        elif res["Squize Momentum"]:
            if True:
                return True
        elif res["Fund master"]:
            if True:
                return True
        elif res["Wolfpack Id"]:
            if True:
                return True

    def get_only_useful_field(self, id_name, values):
        res = {}
        if id_name == "Market Cipher B":
            for field_name, field_values in values.items():
                if field_name == 'Plot_6' \
                        or field_name == 'wt2' \
                        or field_name == 'Plot_5':
                    res[field_name] = field_values
        elif id_name == "VuManChu Cipher B":
            for field_name, field_values in values.items():
                if field_name == 'Buy_Big_green_circle' \
                        or field_name == 'Buy_Big_green_circle__Div' \
                        or field_name == 'GOLD_Buy_Big_GOLDEN_circle' \
                        or field_name == 'Sommi_bullish_flagdiamond' \
                        or field_name == 'Buy_Small_green_dot' \
                        or field_name == 'Sell_Big_red_circle' \
                        or field_name == 'Sell_Big_red_circle__Div' \
                        or field_name == 'Sell_Small_red_dot':
                    res[field_name] = field_values
        elif id_name == "RSI":
            for field_name, field_values in values.items():
                if field_name == 'RSI' or field_name == 'RSIbased_MA':
                    res[field_name] = field_values

        elif id_name == "Squize Momentum":
            for field_name, field_values in values.items():
                if field_name == 'Plot':
                    res[field_name] = field_values
        elif id_name == "Fund master":
            for field_name, field_values in values.items():
                if field_name == 'plotcandle_0_ohlc_high' \
                        or field_name == 'Fund_Master_Bull_Bear_Line':
                    res[field_name] = field_values
        elif id_name == "Wolfpack Id":
            for field_name, field_values in values.items():
                if field_name == 'Plot_2':
                    res[field_name] = field_values
        return res

    async def get_indicators_data(self, range: int, timeframe: str, currency: str):
        res = {}
        for k, v in self.indicatorIds_dict.items():
            response = await self.send_req(self.sessionId, self.sessionSign, range, timeframe, currency, v)
            try:
                res[k] = response[0:10]
            except TypeError as err:
                self.log.error(err)
                return {}

        if await self.test_is_case(currency, timeframe, res):
            result_data = {}
            for k, v in res.items():
                useful = self.get_only_useful_field(k, v[0])
                result_data[k] = useful
            return result_data

    async def get_many_ids(self, req_groups: dict):

        res = {}
        for timeframes, symbols in req_groups.items():
            for tf in timeframes:
                for sym in symbols:
                    idr_res = await self.get_indicators_data(1, tf, sym)
                    if len(idr_res) == 0:
                        continue
                    if res.get(sym, None):
                        res[sym][tf] = idr_res
                    else:
                        res[sym] = {tf: idr_res}

        return res
