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

from parserTelethone.models import Signal, SignalsCompared
from payments.models import Subscription, UserSubscriptions
from api.models import Funding, UserTimeframes


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
    def add_signal(self, time_frame, currency_pair, type, leverage, entry_target, take_profit, stop, title):
        try:
            new_signal = Signal.objects.create(
                time_frame=time_frame, type=type, leverage=leverage,
                currency_pair=currency_pair,
                entry_target=entry_target,
                take_profit=take_profit,
                stop=stop, title=title
            )
        except Exception as e:
            log.exception(e)

    @sync_to_async
    def add_compared_signal(self, time_frame, currency_pair, type, leverage, entry_target, take_profit, stop, title):
        try:
            res = SignalsCompared.objects.create(
                time_frame=time_frame, type=type, leverage=leverage,
                currency_pair=currency_pair,
                entry_target=entry_target,
                take_profit=take_profit,
                stop=stop, title=title
            )
            return res
        except Exception as e:
            log.exception(e)

    @sync_to_async
    def get_signals(self, time_frame, currency_pair, type, datet: datetime):

        signals = [s.to_object() for s in
                   Signal.objects.filter(time_frame=time_frame, currency_pair=currency_pair, type=type)]
        res = []

        for i in signals:
            time_delta = datet - i['created_at']
            duration_in_s = time_delta.total_seconds()
            years = divmod(duration_in_s, 31536000)[0]
            days = time_delta.days
            hours = divmod(duration_in_s, 3600)[0]
            minutes = divmod(duration_in_s, 60)[0]
            seconds = time_delta.seconds

            match time_frame:
                case '5m'| "5м":
                    if years == 0.0 and days == 0 and hours == 0.0 and minutes <= 3:
                        res.append(i)
                case '15m'|"15м":
                    if years == 0.0 and days == 0 and hours == 0.0 and minutes <= 10:
                        res.append(i)
                case '30m'| "30м":
                    if years == 0.0 and days == 0 and hours == 0.0 and minutes <= 25:
                        res.append(i)
                case '1h'| '1ч':
                    if years == 0.0 and days == 0 and hours == 0.0 and minutes <= 50:
                        res.append(i)
                case '4h'| "4м":
                    if years == 0.0 and days == 0 and hours <= 3.0:
                        res.append(i)
                case '1d'| "1д":
                    if years == 0.0 and days == 0 and hours <= 23.0:
                        res.append(i)
                case 'w':
                    if years == 0.0 and days <= 7:
                        res.append(i)
                case 'm':
                    if years == 0.0 and days <= 28:
                        res.append(i)
                case None:
                    if years == 0.0 and days <= 5:
                        res.append(i)

        return res

    @sync_to_async
    def update_signal_status(self, id_signal, status):

        signal = SignalsCompared.objects.get(id=str(id_signal))
        signal.update(is_correct=status)

        return signal

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

    @sync_to_async
    def update_coinglass_currency(self, currency_name, value):
        try:
            res = Funding.objects.get(name=currency_name)
            res.update(default_funding=value)
        except  Funding.DoesNotExist as err:
            new_funding = Funding.objects.create(
                name=currency_name,
                default_funding=value
            )
        return True
    @sync_to_async
    def update_user_timeframes(self, tg_id, value):
        try:

            res = UserTimeframes.objects.get(user__uid=tg_id)
            res.update(timeframe=value)
        except UserTimeframes.DoesNotExist as err:
            tg_profile = TelegramProfile.objects.get(uid=tg_id)
            UserTimeframes.objects.create(
                user=tg_profile,
                timeframe=value
            )
        return True
