import pytz
from datetime import time

from django.conf import settings
from django.utils import timezone
from django.db.models.fields import related

CUSTOM_TZ = pytz.timezone(settings.TIME_ZONE)


def custom_now():
    return timezone.now().astimezone(CUSTOM_TZ)


def to_object(self):
    result = {}

    for f in self._meta.fields:
        if isinstance(f, (related.OneToOneField, related.ForeignKey)):
            value = getattr(self, f.name)
            if value is not None:
                result[f.name] = value.to_object()
        else:
            result[f.name] = getattr(self, f.name)

    for f in self._meta.many_to_many:
        result[f.name] = [obj.to_object() for obj in getattr(self, f.name).all()]

    return result


def merge_times(times: list[tuple[time, time]]):
    times = iter(times)
    merged = next(times).copy()
    for entry in times:
        start, end = entry
        if start <= merged[1]:
            # overlapping, merge
            merged[1] = max(merged[1], end)
        else:
            # distinct; yield merged and start a new copy
            yield merged
            merged = entry.copy()
    yield merged


def get_remote_addr(request) -> str:
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    # if len(x_forwarded_for) > 0:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR', '')
    sock = request._stream.stream.stream.raw._sock
    ip, port = sock.getpeername()
    return f"{ip}:{port}"


def get_data_from_url(get_request) -> dict:
    params = dict(get_request)

    url_data = {}

    if len(params) == 0:
        return {}

    for k, v in params.items():
        if isinstance(v, list):
            if len(v) == 0:
                pass
            elif len(v) == 1:
                url_data[k] = v[0]
            else:
                url_data[k] = v
        else:
            url_data[k] = v
    return url_data
