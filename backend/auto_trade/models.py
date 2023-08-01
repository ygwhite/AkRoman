from django.db.models import (
    Model,
    CharField,
    DateTimeField, TextField,
    BooleanField, IntegerField, ForeignKey, SET_DEFAULT, CASCADE, DO_NOTHING
)

from utils import to_object, custom_now
from customers.models import Customer
from parserTelethone.models import SignalsCompared
from common.models import Currency, AutoDateTimeField


class UserTradeSignal(Model):
    user = ForeignKey(Customer, on_delete=CASCADE, blank=False, null=True)
    signal = ForeignKey(SignalsCompared, on_delete=DO_NOTHING, blank=True, null=False)
    is_trade = BooleanField(default=False, blank=False, null=False)
    is_profit = BooleanField(default=None, blank=False, null=True)
    value_trade = IntegerField(blank=True)
    currency = ForeignKey(Currency, default=1,
                          on_delete=DO_NOTHING, blank=True)
    updated_at = AutoDateTimeField(default=custom_now)
    created_at = DateTimeField(default=custom_now)

    def to_object(self):
        return to_object(self)

    def __repr__(self):
        return f"UserTradeSignal: ({self.user}[{self.signal} {self.is_trade}])"
    def __str__(self):
        return f"{self.value_trade}{self.currency.name} {self.signal.type.title()} {self.created_at.strftime('%d.%m.%Y %H:%M:%S')} "
