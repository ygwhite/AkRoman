from django.db.models import (
    Model,
    CharField,
    DateTimeField, TextField,
    BooleanField,
)

from utils import to_object, custom_now


class Signal(Model):
    time_frame = CharField(unique=False, max_length=6, blank=False, null=True)
    currency_pair = CharField(unique=False, max_length=20, blank=False, null=False)
    type = CharField(unique=False, max_length=10, blank=False, null=False)
    leverage = CharField(unique=False, max_length=10, blank=False, null=True)
    entry_target = CharField(unique=False, blank=False, max_length=50, null=True)
    take_profit = CharField(unique=False, blank=False, max_length=50, null=True)
    stop = CharField(unique=False, blank=False, max_length=50, null=True)
    title = CharField(unique=False, blank=False, max_length=40, null=True)
    created_at = DateTimeField(default=custom_now)

    def to_object(self):
        return to_object(self)

    def __repr__(self):
        return f"Signal: ({self.currency_pair}[{self.time_frame}])"


class SignalsCompared(Model):
    time_frame = CharField(unique=False, max_length=6, blank=True, null=True)
    currency_pair = CharField(unique=False, max_length=20, blank=False, null=False)
    type = CharField(unique=False, max_length=10, blank=False, null=False)
    leverage = CharField(unique=False, max_length=10, blank=False, null=True)
    entry_target = CharField(unique=False, blank=False, max_length=50, null=True)
    take_profit = CharField(unique=False, blank=False, max_length=50, null=True)
    stop = CharField(unique=False, blank=False, max_length=50, null=True)
    is_correct = BooleanField(default=None, blank=True, null=True)
    title = CharField(unique=False, blank=False, max_length=60, null=True)
    created_at = DateTimeField(default=custom_now)

    def to_object(self):
        return to_object(self)

    def __repr__(self):
        return f"Signal: ({self.currency_pair}[{self.time_frame}])"

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()
