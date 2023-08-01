from django.db import models
from customers.models import TelegramProfile


class Funding(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True
    )
    default_funding = models.FloatField()

    def __str__(self):
        return self.name


class Volume(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True,
    )
    price = models.FloatField()
    daily_change = models.IntegerField()
    Volume_daily = models.IntegerField()

    def __str__(self):
        return self.name


class UserTimeframes(models.Model):

    timeframe = models.JSONField()
    user = models.ForeignKey(TelegramProfile, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.timeframe)
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()
