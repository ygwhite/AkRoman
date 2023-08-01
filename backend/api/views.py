import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics

from .models import Funding, Volume
from webapp.models import CurrencyPair, TimeFrame
from api.models import UserTimeframes
from fearandgreedAPI.requests import FearAndGreedAPI
from settings import Fear_And_Greed_API_URL
from settings import BACKEND_LOGGER as log


class CoinAPIView(APIView):
    def get(self, request):
        coins = Funding.objects.all()
        data = {coin.name: coin.default_funding for coin in coins}
        return Response(data)


class VolumeAPIView(APIView):
    def get(self, request):
        volume_data = []
        coins = Volume.objects.all()
        for coin in coins:
            coin_data = [
                coin.name,
                coin.price,
                coin.daily_change,
                coin.Volume_daily,
            ]
            volume_data.append(coin_data)
        return Response(volume_data)


class Timeframe(APIView):
    def get(self, request):
        token = request.query_params.get('order_id')
        print('token:', token)
        fg_index_obj = FearAndGreedAPI(Fear_And_Greed_API_URL, log)
        number = fg_index_obj.get_fear_gred_index()

        timeframes_instance = UserTimeframes.objects.first()
        json_data = timeframes_instance.timeframe
        print(json_data)
        # [
        #     [ “btc”, “usdt”, {“5m”:True, “10m”:True, “15m”:True,“1H”:True,“D”:True, “W”:True}] ,
        # ]

        currencypair = CurrencyPair.objects.order_by('order_num')
        all_timeframes = TimeFrame.objects.all()

        currencypair_data = []
        # добавляем fear and greed первым элементов
        currencypair_data.append(number)
        print(currencypair)
        for currency in currencypair:
            if currency.is_published is True:
                first_curen = currency.first.abbr
                second_curen = currency.last.abbr
                timeframes_data = {def_timeframe.abbr: False for def_timeframe in all_timeframes}
                print(timeframes_data)
                for i in json_data:
                    # если валютные пары совпадают то мы сравниваем таймфреймы
                    if first_curen == i[0] and second_curen == i[1]:

                        for def_timeframe in all_timeframes:
                            # проверяем что проверяемый таймфрейм есть в пользовательских таймфреймах
                            # todo как тут abbr взять
                            if i[2].get(def_timeframe.abbr):
                                timeframes_data[def_timeframe.abbr] = True
                            else:
                                timeframes_data[def_timeframe.abbr] = False

                    else:
                        timeframes_data = {def_timeframe.abbr: False for def_timeframe in all_timeframes}
            else:
                continue

            currencypair_list = []
            currencypair_list.append(first_curen)
            currencypair_list.append(second_curen)
            currencypair_list.append(timeframes_data)
            currencypair_data.append(currencypair_list)

        return Response(currencypair_data)
