import csv
from django.http import HttpResponse
from django.contrib.admin import site
from .models import Subscription, UserSubscriptions
from django.contrib.admin import ModelAdmin



class SubscriptionAdmin(ModelAdmin):
    list_display = "name", "day", "price"

class UserSubscriptionsAdmin(ModelAdmin):
    list_display = "user", "subscription_name",

    def user(self, user):
        return user
    def subscription_name(self, subscription_name):
        return f"{subscription_name.name } ({subscription_name.day})"

site.register(Subscription, SubscriptionAdmin)
site.register(UserSubscriptions, UserSubscriptionsAdmin)
