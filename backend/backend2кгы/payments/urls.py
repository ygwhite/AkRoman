from django.urls import path

from .views import postback_ссp

urlpatterns = [
    path("cryptocloud_pb", postback_ссp),
]
