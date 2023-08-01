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


@csrf_exempt
@async_to_sync
async def postback_ссp(request, *args, **kwargs):
    # /postback?reg=true&ftd=false&dep=false&click_id=43253245&site_id=23232323&trader_id=38718189&sumdep=
    default_response = HttpResponse("", status=200)
    data_dics = json.loads(request.body)
    telegram_id = int(data_dics['order_id'].split('S')[0])
    days = int(data_dics['order_id'].split('S')[1])
    bot = Bot(token=TELEGRAM_API_TOKEN)
    if data_dics['status'] == 'success':

        subs_lst = await bi.get_subscriptions()

        for sub in subs_lst:
            if sub['day'] == days:
                customer = await bi.get_customer(telegram_id)
                added_pay = await bi.add_pay_subscription(telegram_id, sub['id'])

                await bot.send_message(telegram_id, f"Subscription for {days} is payed")
                return default_response

        await bot.send_message(telegram_id, f"Subscription for {days} isn't success - contact support")
        print(telegram_id, days)
    else:
        await bot.send_message(telegram_id, f"Subscription for {days} isn't success - contact support")
    return default_response