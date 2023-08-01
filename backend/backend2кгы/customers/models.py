from django.db.models import (
    Model,
    BooleanField,
    CharField,
    DateTimeField,
    FloatField,
    ForeignKey,
    IntegerField,
    OneToOneField,
    CASCADE,
    SET_DEFAULT,
    SET_NULL, TextField
)
from django.dispatch import receiver
from django.db.models.signals import post_delete

from common.models import Currency, AutoDateTimeField

from utils import custom_now, to_object

from webapp.models import TimeFrame


class Customer(Model):
    created_at = DateTimeField(default=custom_now)
    updated_at = AutoDateTimeField(default=custom_now)
    tg_profile = OneToOneField("TelegramProfile", unique=True, on_delete=CASCADE, blank=False, null=False)

    def to_object(self):
        customer = to_object(self)
        customer['timeframes'] = self.get_available_timeframes()
        customer['timeframes.abbr'] = self.get_available_timeframes(key="abbr")
        return customer

    def get_available_timeframes(self, key=None):

        sorted_timeframes = sorted(TimeFrame.objects.all(),
                                   key=lambda t: int(t.to_minutes()))

        if key is None:
            return [t.to_object() for t in sorted_timeframes]
        else:
            return [getattr(t, key) for t in sorted_timeframes]

    def __str__(self):
        return self.tg_profile.first_name

    def __repr__(self):
        return f"Customer({self.tg_profile.uid})"

    def update(self, **kwargs):
        for key, value in kwargs.items():
            match key:


                case "tg_profile":
                    kwargs = value
                    self.tg_profile.update(**kwargs)

                case _:
                    setattr(self, key, value)

        self.save()

    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


@receiver(post_delete, sender=Customer)
def customer_post_delete(sender, *args, **kwargs):
    """
    https://stackoverflow.com/questions/12754024/onetoonefield-and-deleting
    """
    customer = kwargs.get("instance")

    if customer.tg_profile is not None:
        customer.tg_profile.delete()


class TelegramProfile(Model):
    created_at = DateTimeField(default=custom_now)
    updated_at = AutoDateTimeField(default=custom_now)
    uid = CharField(unique=True, max_length=20, blank=False, null=False)
    binance_api_key = CharField(unique=True, max_length=100, blank=True, null=True)
    binance_secret_key = CharField(unique=True, max_length=100, blank=True, null=True)
    ref_id = CharField(unique=False, max_length=30, blank=True, null=True)
    first_name = CharField(max_length=50, default="", blank=True, null=False)
    last_name = CharField(max_length=50, default="", blank=True, null=False)
    username = CharField(max_length=50, default="", blank=True, null=True)
    language_code = CharField(max_length=4, blank=False, null=False)
    language = CharField(max_length=10, blank=False, null=False, default="english")
    is_allowed = BooleanField(default=True, blank=False, null=False)
    is_admin = BooleanField(default=False, blank=False, null=False)

    def to_object(self):
        return to_object(self)

    def __str__(self):
        return self.uid

    def __repr__(self):
        return f"TelegramProfile({self}, " \
               f"{self.username}, {self.is_allowed}, {self.is_admin})"

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()
