from django.contrib.admin import SimpleListFilter


class TgAllowedFilter(SimpleListFilter):
    title = "Is allowed"
    parameter_name = "tg_profile__is_allowed"

    def lookups(self, request, model_admin):
        return (
            (True, 'Allowed'),
            (False, 'Banned')
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(tg_profile__is_allowed=self.value())


class TgAdminFilter(SimpleListFilter):
    title = "Is admin"
    parameter_name = "tg_profile__is_admin"

    def lookups(self, request, model_admin):
        return (
            (True, 'Admin'),
            (False, 'Not admin')
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(tg_profile__is_admin=self.value())


class CurrencyFilter(SimpleListFilter):
    title = "Currency"
    parameter_name = "currency"

    def lookups(self, request, model_admin) -> list[tuple]:
        queryset = model_admin.get_queryset(request)
        abbrs = set()
        for item in queryset:
            abbrs.add(item.currency.abbr)
        return [(abbr, abbr) for abbr in sorted(abbrs)]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(currency__abbr=self.value())
