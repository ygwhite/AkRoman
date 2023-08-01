from django.contrib.admin import site
from .model_admins import (
    CustomerAdmin,
    TelegramProfileAdmin,
)
from ..models import (
    Customer,
    TelegramProfile,
)

site.site_header = "Backend Admin Panel"

site.register(Customer, CustomerAdmin)
site.register(TelegramProfile, TelegramProfileAdmin)
