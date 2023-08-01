from django.db.models import (
    Model,
    CharField,
    DateTimeField,
)

from utils import to_object, custom_now


class AutoDateTimeField(DateTimeField):
    def pre_save(self, *args, **kwargs):
        return custom_now()


class Currency(Model):
    abbr = CharField(unique=True, max_length=8, blank=False, null=False)
    name = CharField(max_length=50, blank=True, null=False)

    def to_object(self):
        return to_object(self)

    def __str__(self):
        return self.abbr

    def __repr__(self):
        return f"Currency({self.abbr})"
