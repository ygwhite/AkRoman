from django.contrib.admin import site, ModelAdmin

from .models import Funding, Volume, UserTimeframes


class FundingAdmin(ModelAdmin):
    list_display = 'name', 'default_funding'


class VolumeAdmin(ModelAdmin):
    list_display = 'name', 'price', 'daily_change', 'Volume_daily'


class TimeframesAdmin(ModelAdmin):
    list_display = 'timeframe', 'user'


site.register(Funding, FundingAdmin)
site.register(Volume, VolumeAdmin)
site.register(UserTimeframes, TimeframesAdmin)
