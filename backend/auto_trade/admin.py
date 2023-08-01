import csv
from django.http import HttpResponse
from django.contrib.admin import site
from .models import UserTradeSignal
from django.contrib.admin import ModelAdmin


class UserTradeSignalAdmin(ModelAdmin):
    list_display = "user", "signal", "is_trade", "updated_at", "created_at"

    def user(self, user):
        return user


site.register(UserTradeSignal, UserTradeSignalAdmin)
