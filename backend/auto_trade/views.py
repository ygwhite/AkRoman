import json
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
from customers.models import Customer
from aiogram import Bot, Dispatcher
from settings import BACKEND_LOGGER as log
from settings import TELEGRAM_API_TOKEN

from interface.backend import BackendInterface

bi = BackendInterface()
