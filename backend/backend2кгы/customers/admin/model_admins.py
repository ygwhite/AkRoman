from django.contrib.admin import ModelAdmin
from .filters import (
    CurrencyFilter,
    TgAdminFilter,
    TgAllowedFilter
)
from common.admin import ExportCsvMixin


class CustomerAdmin(ModelAdmin, ExportCsvMixin):
    actions = "export_as_csv",
    list_display = "tg_profile", "tg_allowed", "tg_admin", "created_at", "updated_at"
    list_filter = "created_at", TgAllowedFilter, TgAdminFilter
    readonly_fields = "created_at", "updated_at"

    # change_list_template = "admin/customers/customers_change_list.html"

    def tg_allowed(self, customer):
        return customer.tg_profile.is_allowed

    def tg_admin(self, customer):
        return customer.tg_profile.is_admin


class TelegramProfileAdmin(ModelAdmin, ExportCsvMixin):
    actions = "export_as_csv",
    list_display = "uid", "first_name", "last_name", "username","ref_id", "language", "is_allowed", "is_admin", "created_at", "updated_at",
    list_filter = "is_allowed", "is_admin", "language_code", "created_at", "updated_at",
    readonly_fields = "created_at", "updated_at",










