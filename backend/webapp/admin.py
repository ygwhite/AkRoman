from django.contrib.admin import site, ModelAdmin

from .models import TimeFrame, TimeWindow, CurrencyPair, IndicatorForTimeFrame, Indicator, ChartForTimeFrame

from utils import merge_times


class CurrencyPairAdmin(ModelAdmin):
    list_display = ("pair", "merged_time_windows", "order_num", 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published',)

    def pair(self, currency_pair):
        try:
            return currency_pair.first.abbr + currency_pair.last.abbr
        except Exception as err:
            if currency_pair.first is None:
                return currency_pair.last.abbr
            else:
                return currency_pair.first.abbr

    def merged_time_windows(self, currency_pair):
        tws = currency_pair.time_window.all()

        if len(tws) == 1:
            return str(tws.first())
        else:
            times = [[tw.start, tw.stop] for tw in tws]
            merged_times = merge_times(times)
            return ", ".join((" - ".join(map(str, tw)) for tw in merged_times))


class TimeFrameAdmin(ModelAdmin):
    list_display = "abbr", "name"


class IndicatorForTimeFrameAdmin(ModelAdmin):
    list_display = "time_frame", "get_indicators"

    def get_indicators(self, indicator_for_timeframe):
        return ", ".join(map(str, indicator_for_timeframe.indicators.all()))


class ChartForTimeFrameAdmin(ModelAdmin):
    list_display = "currency_pair", "time_frame", "link"

    def get_currency_pair(self, ChartForTimeFrame):
        return ", ".join(map(str, ChartForTimeFrame.indicators.all()))


site.register(TimeFrame, TimeFrameAdmin)
site.register(TimeWindow)
site.register(CurrencyPair, CurrencyPairAdmin)
site.register(ChartForTimeFrame, ChartForTimeFrameAdmin)
# site.register(Indicator)
