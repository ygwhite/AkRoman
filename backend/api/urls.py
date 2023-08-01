from django.urls import path
from .views import CoinAPIView, VolumeAPIView, Timeframe

urlpatterns = [
    path('api/funding_data/', CoinAPIView.as_view(), name='funding_data_api'),
    path('api/volume_data/', VolumeAPIView.as_view(), name='volume_data_api'),
    path('api/timeframe_data/', Timeframe.as_view(), name='timeframe_data_api'),
]
