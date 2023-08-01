class Timeframe(APIView):
    def get(self, request):
        fg_index_obj = FearAndGreedAPI(Fear_And_Greed_API_URL, log)
        number = fg_index_obj.get_fear_gred_index()

        timeframes_instance = UserTimeframes.objects.first()
        json_data = timeframes_instance.timeframe
        # [
        #     [ “btc”, “usdt”, {“5m”:True, “10m”:True, “15m”:True,“1H”:True,“D”:True, “W”:True}] ,
        # ]

        currencypair = CurrencyPair.objects.order_by('order_num')
        all_timeframes = TimeFrame.objects.all()

        currencypair_data = []
        # добавляем fear and greed первым элементов
        currencypair_data.append(number)
        for currency in currencypair:
            first_curen = currency.first.abbr
            second_curon = currency.last.abbr
            timeframes_data = {}
            for i in json_data:
                # если валютные пары совпадают то мы сравниваем таймфреймы
                if first_curen == i[0] and second_curon == i[1]:

                    for def_timeframe in all_timeframes:
                        # проверяем что проверяемый таймфрейм есть в пользовательских таймфреймах
                        # todo как тут abbr взять
                        if i[3][def_timeframe['abbr']]:
                            timeframes_data[def_timeframe['abbr']] = True
                        else:
                            timeframes_data[def_timeframe['abbr']] = False

                else:
                    timeframes_data = {def_timeframe['abbr']: False for def_timeframe in all_timeframes}

            currencypair_list = []
            currencypair_list.append(currency.first.abbr)
            currencypair_list.append(currency.last.abbr)
            currencypair_list.append(timeframes_data)
            currencypair_data.append(currencypair_list)
        return Response(currencypair_data)
