import datetime
import datetime as dt

from asgiref.sync import sync_to_async
from aiogram.types import User

from settings import BACKEND_LOGGER as log
from customers.models import (
    Customer,
    TelegramProfile,
)
from webapp.models import CurrencyPair

from webapp.models import IndicatorForTimeFrame

from webapp.models import ChartForTimeFrame

from payments.models import Subscription, UserSubscriptions


class BackendInterface:
    __slots__ = ()

    # -- Synchronous methods --
    def __get_customer(self, tg_uid: str) -> dict | None:
        customer = Customer.objects.get(tg_profile__uid=str(tg_uid))
        return customer.to_object()

    def is_customer(self, tg_uid: str) -> bool:
        try:
            customer = Customer.objects.get(tg_profile__uid=str(tg_uid))
            return True
        except Exception as err:
            return False

    @sync_to_async
    def get_tf_indicators(self, tf_abbr) -> dict | None:
        res = {'abbr': tf_abbr, 'indicators': []}
        try:
            customer = IndicatorForTimeFrame.objects.get(time_frame__abbr=str(tf_abbr))
        except Exception as err:
            return res
        cus_obj = customer.to_object()

        indicators = [i['name'].strip() for i in cus_obj['indicators']]
        res['indicators'] = indicators
        return res

    def __get_or_create_customer(self, user: User) -> bool:
        try:
            return self.__get_customer(user.id)
        except Customer.DoesNotExist:
            pass

        try:
            try:
                tg_profile = TelegramProfile.objects.get(uid=user.id)
            except TelegramProfile.DoesNotExist:
                tg_profile = TelegramProfile.objects.create(
                    uid=user.id,
                    first_name=getattr(user, "first_name", "") or "",
                    last_name=getattr(user, "last_name", "") or "",
                    username=getattr(user, "username", "") or "",
                    language_code=user.language_code,
                )

            Customer.objects.create(
                tg_profile=tg_profile,
            )

            return self.__get_customer(user.id)
        except Exception as e:
            log.exception(e)

        return None

    def __get_tg_profile(self, tg_uid: str):
        tg_profile = TelegramProfile.objects.get(uid=tg_uid)
        return tg_profile.to_object()

    # def update_language(self, tg_uid, new_language):

    @sync_to_async
    def get_allcurrencypairs(self):
        try:
            return [s.to_object() for s in CurrencyPair.objects.all()]
        except Exception as err:
            print(err)
            return []

    @sync_to_async
    def get_timeframe_links(self):
        try:
            return [s.to_object() for s in ChartForTimeFrame.objects.all()]
        except Exception as err:
            print(err)
            return []

    @sync_to_async
    def update_currencypair(self, cur, pct):
        cur.update(pct=str(pct))
        return False

    def __get_user_group_ids(self, query: str):
        group = None

        match query:
            case "no_id":
                group = Customer.objects.filter(qt_profile=None)
            case "no_dep":
                group = Customer.objects.filter(balance__amount=0)
            case _:
                group = Customer.objects.filter(status__name=query)

        if len(group) == 0:
            return []

        return [c.tg_profile.uid for c in group if c.tg_profile is not None]

    def __update_customer(self, tg_uid: str, **kwargs):
        customer = Customer.objects.get(tg_profile__uid=tg_uid)
        customer.update(**kwargs)
        return self.__get_customer(tg_uid)

    # -- Asynchronous methods --
    async def connect(self):
        pass

    @sync_to_async
    def get_tg_profile(self, tg_uid: str):
        return self.__get_tg_profile(tg_uid)

    @sync_to_async
    def get_customer(self, tg_uid: str):
        return self.__get_customer(tg_uid)

    @sync_to_async
    def get_or_create_customer(self, user: User):
        return self.__get_or_create_customer(user)

    @sync_to_async
    def update_customer(self, tg_uid: str, **kwargs):
        return self.__update_customer(tg_uid, **kwargs)

    @sync_to_async
    def get_status_list(self):
        return self.__get_status_list()

    @sync_to_async
    def get_user_group_ids(self, query: str):
        return self.__get_user_group_ids(query)

    @sync_to_async
    def get_subscriptions(self):
        try:
            return [s.to_object() for s in Subscription.objects.all()]
        except Exception as err:
            print(err)
            return []

    @sync_to_async
    def get_test_subscription(self):
        try:
            all_subs = [s.to_object() for s in Subscription.objects.all()]
        except Exception as err:
            log.exception(err)
            return []

        for sub in all_subs:
            if sub['name'].lower() == 'test':
                return sub

    @sync_to_async
    def add_pay_subscription(self, tg_id, subscription_id):
        customer = Customer.objects.get(tg_profile__uid=str(tg_id))
        # customer_id = customer['id']
        sub_obj = Subscription.objects.get(id=str(subscription_id))
        try:
            res = UserSubscriptions.objects.update_or_create(
                user=customer,
                subscription_name=sub_obj
            )

            return res
        except Exception as e:
            log.exception(e)

    @sync_to_async
    def get_user_subs(self, uid):
        try:
            return [s.to_object() for s in UserSubscriptions.objects.filter(user__tg_profile__uid=uid)]
        except Exception as err:
            print(err)
            return []

    @sync_to_async
    def remove_pay_subscription(self, usr_subscription_id):
        try:
            sub = UserSubscriptions.objects.get(id=str(usr_subscription_id))
            sub.delete()

        except Exception as e:
            log.exception(e)

    # BINANCE API
    @sync_to_async
    def update_binance_api_key(self, tg_id, api_key):

        res = self.__update_customer(tg_id, tg_profile={'binance_api_key': api_key})

        return True

    @sync_to_async
    def update_binance_secret_key(self, tg_id, secret_key):

        res = self.__update_customer(tg_id, tg_profile={'binance_secret_key': secret_key})
        return True
