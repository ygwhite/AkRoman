from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    ManyToManyField,
    TimeField, IntegerField, BooleanField,
    SET_DEFAULT, OneToOneField, SET_NULL, CASCADE,
)

from common.models import Currency

from utils import to_object, custom_now


class TimeFrame(Model):
    abbr = CharField(unique=True, max_length=4, blank=False, null=False)
    name = CharField(max_length=50, blank=False, null=False)

    def to_object(self):
        return to_object(self)

    def to_minutes(self):
        match self.name:
            case '1m':
                return 1
            case "5m":
                return 5
            case "30m":
                return 30
            case "15m":
                return 15
            case "1H":
                return 60
            case "4H":
                return 240
            case "D":
                return 720
            case "W":
                return 1000
            case _:
                return 10000

    def __str__(self):
        return self.abbr

    def __repr__(self):
        return f"TimeFrame({self.abbr})"


class Indicator(Model):
    name = CharField(max_length=50, blank=False, null=False)

    def to_object(self):
        return to_object(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Indicator: ({self.__str__()})"


class IndicatorForTimeFrame(Model):
    time_frame = OneToOneField("TimeFrame", default=1,
                               on_delete=CASCADE, blank=False, null=False, unique=True)
    indicators = ManyToManyField(Indicator, blank=False)

    def to_object(self):
        return to_object(self)

    def __repr__(self):
        idc = ", ".join(map(str, self.indicators.all()))
        return f"IDC For TF: ({self.__str__()}[{idc}])"


class TimeWindow(Model):
    start = TimeField(blank=False, null=False)
    stop = TimeField(blank=False, null=False)

    def to_object(self):
        return to_object(self)

    def __str__(self):
        return f"{self.start} - {self.stop}"

    def __repr__(self):
        return f"TimeWindow({self.__str__()})"


class CurrencyPair(Model):
    first = ForeignKey(Currency, related_name="currencypair1_set", default=1, on_delete=SET_DEFAULT, blank=False,
                       null=False)
    last = ForeignKey(Currency, related_name="currencypair2_set", default=2, on_delete=SET_DEFAULT, blank=True,
                      null=True)
    time_window = ManyToManyField(TimeWindow, blank=False)
    order_num = IntegerField(null=True, blank=True)
    is_published = BooleanField(default=True, verbose_name='Показывать пары')

    def to_object(self):
        return to_object(self)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    @property
    def is_available(self):
        return any(tw.start <= custom_now().time() <= tw.stop for tw in self.time_window.all())

    def __str__(self):
        return f"{self.first}{self.last}"

    def __repr__(self):
        time_windows = ", ".join(map(str, self.time_window.all()))
        return f"CurrencyPair({self.__str__()}, [{time_windows}])"


class ChartForTimeFrame(Model):
    time_frame = ForeignKey("TimeFrame", default=1,
                            on_delete=CASCADE, blank=False, null=False)
    currency_pair = ForeignKey(CurrencyPair, on_delete=CASCADE, blank=False)
    link = CharField(unique=True, max_length=30, blank=True)

    def to_object(self):
        return to_object(self)

    def __repr__(self):
        return f"IDC For TF: ({self.__str__()}[{self.link}])"
