import datetime
import json
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from customers.models import Customer
from .models import CurrencyPair

from utils import decrypt, get_data_from_url
from settings import BACKEND_LOGGER as log, WSS_URL, WSS_HTTPS_URL, Fear_And_Greed_API_URL, COINGLASS_API_URL, \
    COINGLASS_LOGGER, COINGLASS_API_KEY
from django.template.defaulttags import register
from fearandgreedAPI.requests import FearAndGreedAPI

from coinglassAPI.requests import CoinglassAPI


@register.filter(name='lookup')
def lookup(value, arg):
    print(value.get(arg))
    return value.get(arg)


@csrf_exempt
@xframe_options_exempt
def menu(request, *args, **kwargs):
    context = {
        "wss_url": WSS_HTTPS_URL
    }
    default_response = render(request, "oops.html", {})

    if request.method == "GET":
        # Проверяем, что пользователь открыл страницу в telegram
        url_params = get_data_from_url(request.GET)
        hello = url_params.get("hello")

        if hello is None:
            log.warning("Отсутствует url параметр hello")
            return default_response

        # Получаем зашифрованное значение tg_uid из url параметра hello
        try:
            json_str = decrypt(hello)
            data = json.loads(json_str)
        except Exception as e:
            log.exception(e)
            return default_response

        if data.get("tg_uid") is None:
            log.warning("Отсутствует tg_uid в данных url параметра hello")
            return default_response

        tg_uid = data["tg_uid"]

        # Находим customer по tg_uid
        try:
            customer = Customer.objects.get(tg_profile__uid=tg_uid)
        except Customer.DoesNotExist:
            log.warning(f"Customer {tg_uid} was not found")
            return default_response

        # Пакуем контекст
        context["customer"] = customer
        context["timeframes"] = customer.get_available_timeframes()
        if len(context["timeframes"]) > 0:
            context["initial_tf"] = context["timeframes"][0]
        all_currencypairs = CurrencyPair.objects.all()
        available_pairs = [cp for cp in all_currencypairs if
                           cp.is_available and cp.last.abbr.lower().find('lqvd') == -1]
        not_avalable_currencies = [cp for cp in all_currencypairs if
                                   not cp.is_available]

        available_pairs_ordered = [pair for pair in all_currencypairs if
                                   pair.order_num and pair.last.abbr.lower().find('lqvd') == -1]
        available_pairs_not_ordered = [pair for pair in all_currencypairs if
                                       not pair.order_num and pair.last.abbr.lower().find('lqvd') == -1]
        available_luquidity = [pair for pair in all_currencypairs if pair.last.abbr.lower().find('lqvd') > -1]

        available_pairs_ordered_sorted = sorted(available_pairs_ordered, key=lambda x: x.order_num)

        context["currency_pairs"] = available_pairs_ordered_sorted + available_pairs_not_ordered
        context["available_luquidity"] = available_luquidity
        context["available_luquidity_timeframes"] = [tf for tf in context["timeframes"] if tf['abbr'] == 'D']
        context["not_avalable_currencies"] = not_avalable_currencies

        if len(available_pairs) > 0:
            context["initial_cp"] = available_pairs[0]
        fg_index_obj = FearAndGreedAPI(Fear_And_Greed_API_URL, log)
        context["fear_greed_index"] = fg_index_obj.get_fear_gred_index()
        coinglass_obj = CoinglassAPI(COINGLASS_API_URL,COINGLASS_API_KEY, COINGLASS_LOGGER)
        context["coinglass_funding_rates"] = coinglass_obj.get_funding_rates()

        # check for weekend - sleep page if True
        # if datetime.datetime.now().weekday() >= 5:
        #     context["sleep_page"] = True

        response = render(request, "menu.html", context)

        # response["Access-Control-Allow-Origin"] = "*"
        # response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
        # response["Access-Control-Max-Age"] = "0"
        # response["Content-Security-Policy"] = "default-src *; connect-src *; script-src *; object-src *;"
        # response["X-Content-Security-Policy"] = "default-src *; connect-src *; script-src *; object-src *;"
        # response["X-Webkit-CSP"] = "default-src *; connect-src *; script-src 'unsafe-inline' 'unsafe-eval' *; object-src *;"
        # TODO заменить xframe_options_exempt на заголовки для безопасного отображения в iframe
        return response

    return default_response
