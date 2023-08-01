from django.db.models import (
    Model,
    CharField,
    DateTimeField, TextField,
    BooleanField, IntegerField, ForeignKey, SET_DEFAULT, CASCADE, DO_NOTHING
)

from utils import to_object, custom_now
from customers.models import Customer


class Subscription(Model):
    name = CharField(unique=False, max_length=20, null=False)
    day = IntegerField(unique=False, null=False)
    price = IntegerField(unique=False, null=False)
    created_at = DateTimeField(default=custom_now)

    def to_object(self):
        return to_object(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Subscription: ({self.name}[{self.day}])"


class UserSubscriptions(Model):
    user = ForeignKey(Customer, on_delete=CASCADE, blank=True, null=True)
    subscription_name = ForeignKey(Subscription, on_delete=DO_NOTHING,
                                   null=False)

    created_at = DateTimeField(default=custom_now)

    def to_object(self):
        return to_object(self)

    def __repr__(self):
        return f"Subscriptions history: ({self.user}[{self.subscription_name}])"
