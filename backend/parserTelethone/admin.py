import csv
from django.http import HttpResponse
from django.contrib.admin import site
from .models import Signal, SignalsCompared
from django.contrib.admin import ModelAdmin


class SignalAdmin(ModelAdmin):
    list_display = "time_frame", "currency_pair", 'type', 'title', "created_at"


class SignalComparedAdmin(ModelAdmin):
    list_display = "time_frame", "currency_pair", 'type', 'title', "is_correct", "created_at"


site.register(Signal, SignalAdmin)

site.register(SignalsCompared, SignalComparedAdmin)
