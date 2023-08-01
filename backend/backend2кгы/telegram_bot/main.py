import copy
import datetime
import re
import json
from time import time
from uuid import uuid4
from asyncio import sleep
from django.core.exceptions import ObjectDoesNotExist
from aiogram import executor, Dispatcher
from aiogram.types import (
    User,
    Message,
    MediaGroup,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.types.input_file import InputFile
from aiogram.types.message import ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.exceptions import BotBlocked
from loguru._logger import Logger
import websockets
from telegram_bot.langs_support import TextsManager

from settings import (
    REG_LIFETIME,
    DEP_LIFETIME,
    TELEGRAM_MEDIA_PATH,
    BACKEND_ADMIN_URL,
    POSTBACK_SIMULATE_REG,
    POSTBACK_SIMULATE_DEP,
    WSS_URL, WSS_BOT_URL,
    TELEGRAM_LOGGER as log,
    COINGLASS_LOGGER, COINGLASS_API_URL, COINGLASS_API_KEY
)

from telegram_bot.keyboards.keyboards import KeyboardManager

from payments.utils import get_user_active_subs

from coinglassAPI.requests import CoinglassAPI
from utils import encrypt
from interface.backend import BackendInterface
from chartimg.requests import ChartImgAPI
from binanceOrderbook.requests import BinanceOrderbook
from cryptoBubbles.requests import CryptoBubbleAPI
from payments.requests import PaymentsAPI
from webapp.models import CurrencyPair


def permission(*permissions: str):
    def decorator(method):
        async def wrapper(self, tgobject, *args, **kwargs):

            user = tgobject.from_user

            try:
                tg_profile = await self.bi.get_tg_profile(user.id)
                is_test_sub = False
            except ObjectDoesNotExist as e:
                is_test_sub = True
                rm = KeyboardManager.lang_select_buttons()
                txt = TextsManager.first_message('english')
                await tgobject.reply(txt, reply_markup=rm)

            customer = await self.bi.get_or_create_customer(user)
            # Если юзер новый - мы ему даем тестовую подписку
            if is_test_sub:
                log.debug(f"User has test sub (id: {user.id})")
                test_sub = await self.bi.get_test_subscription()
                await self.bi.add_pay_subscription(user.id, test_sub['id'])
            user_sub = await self.bi.get_user_subs(user.id)
            check_user_sub = await get_user_active_subs(user_sub, self.bi)
            if not check_user_sub:
                text = TextsManager.without_sub_txt(customer['tg_profile']['language'])
                if type(tgobject) is Message:
                    await tgobject.reply(text)
            if customer is None:
                raise Exception(f"Не удалось создать пользователя (id: {user.id})")
            log.debug(f"Проверка прав пользователя (id: {user.id})")

            for permission in permissions:
                match permission:
                    case "tg_allowed":
                        if customer.get("tg_profile", {}).get("is_allowed", True) == False:
                            log.debug(f"В доступе отказано [(tg_allowed, False)] (id: {user.id})")
                            return None

                    case "tg_admin":
                        if customer.get("tg_profile", {}).get("is_admin", False) == False:
                            log.debug(f"В доступе отказано [(tg_admin, False)] (id: {user.id})")
                            return None

                    case "payed":
                        if not check_user_sub:
                            return None

            log.debug(f"Доступ разрешен (id: {user.id})")
            return await method(self, tgobject, *args, **kwargs)

        return wrapper

    return decorator


class BotService:
    __slots__ = "dp", "bot", "bi", "cr", "cb", 'bo', "webapp_link", "pm", "log", "websockets"

    class BotState(StatesGroup):
        __slots__ = ()

        admin = State()
        binance_api_key = State()
        binance_secret_key = State()
        support = State()
        main = State()
        reg = State()
        select_lang = State()
        dep = State()
        monitoring = State()

    def __init__(self,
                 dp: Dispatcher,
                 webapp_link: str,
                 bi: BackendInterface,
                 cr: ChartImgAPI,
                 cb: CryptoBubbleAPI,
                 bo: BinanceOrderbook,
                 pm: PaymentsAPI,
                 log: Logger):

        self.dp = dp
        self.bot = dp.bot
        self.bi = bi
        self.cr = cr
        self.cb = cb
        self.bo = bo
        self.pm = pm
        self.webapp_link = webapp_link
        self.websockets = dict()
        self.log = log

    async def init_conversation(self, user: User, state: FSMContext):
        """Начало диалога с новым пользователем"""
        self.log.debug(f"Начат новый диалог (id: {user.id})")

        await self.BotState.main.set()

        text = f"Привет, {user.first_name}! 👋 "
        await self.bot.send_message(user.id, text)

    @log.catch
    @permission("tg_allowed")
    async def handle_cmd_start(self, message: Message,
                               state: FSMContext, *args, **kwargs):
        """Обработчик команды `/start`"""

        user = message.from_user
        coinglass_obj = CoinglassAPI(COINGLASS_API_URL, COINGLASS_API_KEY, COINGLASS_LOGGER)
        coinglass_obj.get_funding_rates()
        self.log.debug(f"Вызвана команда `/start` (id: {user.id})")
        await state.finish()
        # binance_orderbook_text = await self.bo.get_orderbook_text('BTCUSDT')

        await self.stop_monitoring(user, state)
        await self.bi.connect()

        state = self.dp.current_state(chat=user.id, user=user.id)

        tg_profile = await self.bi.get_tg_profile(user.id)

        async with state.proxy() as data:
            data["session_id"] = str(uuid4())

        commands = TextsManager.bot_command(tg_profile['language'])

        if tg_profile['is_admin'] == True:
            commands.append(BotCommand('admin', "Панель администратора"))

        await self.dp.bot.set_my_commands(commands)
        await self.resolve_init_restart(user, state)

    async def resolve_init_restart(self, user, state):
        """Маршрутизатор состояния диалога после перезагрузки"""

        customer = await self.bi.get_customer(user.id)

        await self.init_menu(user, state)

    async def init_menu(self, user: User, state: FSMContext, only_keyboard=False):
        "Функция возвращает пользователя к этапу когда он успешно внес депозит"

        await self.BotState.dep.set()

        url_data = encrypt(json.dumps({
            "tg_uid": str(user.id),
        }))
        webapp_menu_link = f"{self.webapp_link}/menu?hello={url_data}"

        if only_keyboard:
            return
        tg_profile = await self.bi.get_tg_profile(user.id)
        text = TextsManager.menu_text(tg_profile['language'])
        rm = KeyboardManager.menu_buttons(webapp_menu_link, tg_profile['language'])
        await self.bot.send_message(
            user.id,
            text,
            reply_markup=rm
        )

    @log.catch
    @permission("tg_allowed")
    async def handle_cmd_support(self, message: Message,
                                 state: FSMContext, *args, **kwargs):
        """Обработчик команды `/support`"""

        # await self.BotState.support.set()

        user = message.from_user
        self.log.debug(f"Вызвана команда `/support` (id: {user.id})")

        await self.stop_monitoring(user, state)
        tg_profile = await self.bi.get_tg_profile(user.id)

        text = TextsManager.support_reply_text(tg_profile['language'])

        await message.reply(
            text
        )

    @log.catch
    @permission("tg_allowed", "tg_admin")
    async def handle_cmd_admin(self, message: Message,
                               state: FSMContext, *args, **kwargs):
        """Обработчик команды `/admin`"""
        user = message.from_user
        self.log.debug(f"Вызвана команда `/admin` (id: {user.id})")

        await self.stop_monitoring(user, state)
        await self.init_admin(user)

    async def init_admin(self, user):
        """Возврат к вызову команды `/admin`"""
        await self.BotState.admin.set()

        btn_admin = InlineKeyboardButton(
            'Админ панель django',
            url=BACKEND_ADMIN_URL
        )

        ikm_admin = InlineKeyboardMarkup()
        ikm_admin.add(btn_admin)

        text = "Добро пожаловать в админку"
        await self.bot.send_message(
            user.id,
            text,
            reply_markup=ReplyKeyboardRemove()
        )

        text = "Нажмите на кнопку, чтобы выбрать действие."
        await self.bot.send_message(user.id, text, reply_markup=ikm_admin)

    @log.catch
    @permission("tg_allowed")
    async def handle_btn_profile(self, msg: Message,
                                 state: FSMContext, *args, **kwargs):
        """Обработчик кнопки \"Профиль\""""

        user = msg.from_user

        customer = await self.bi.get_customer(user.id)

        timeframes = [t['abbr'] for t in customer['timeframes']]
        user_sub = await self.bi.get_user_subs(user.id)
        active_user_sub = await get_user_active_subs(user_sub, self.bi)
        active_user_sub = [i['subscription_name']['name'] for i in active_user_sub]
        is_binance_api = bool(customer['tg_profile']['binance_secret_key'])

        text = TextsManager.profile(customer['tg_profile']['language'], timeframes, active_user_sub, is_binance_api)

        rm = KeyboardManager.in_profile_buttons()
        await self.bot.send_message(
            user.id,
            text, reply_markup=rm
        )

    @log.catch
    @permission("tg_allowed")
    async def handle_connect_binance(self, msg: Message,
                                     state: FSMContext, *args, **kwargs):
        """Обработчик кнопки \"Профиль\""""

        user = msg.from_user
        await self.BotState.binance_api_key.set()
        customer = await self.bi.get_customer(user.id)

        text = TextsManager.binance_enter_api(customer['tg_profile']['language'])

        rm = KeyboardManager.cancel_button_lang(customer['tg_profile']['language'])
        await self.bot.send_message(
            user.id,
            text, reply_markup=rm
        )

    @log.catch
    @permission("tg_allowed")
    async def waiting_binance_api_key(self, msg: Message,
                                      state: FSMContext, *args, **kwargs):
        """Обработчик кнопки pay\""""

        user = msg.from_user
        customer = await self.bi.get_customer(user.id)

        text = TextsManager.binance_api_key_recieved(customer['tg_profile']['language'])
        res = await self.bi.update_binance_api_key(user.id, msg.text)

        rm = KeyboardManager.cancel_button_lang(customer['tg_profile']['language'])
        await self.bot.send_message(
            user.id,
            text, reply_markup=rm
        )
        await msg.delete()
        await self.BotState.binance_secret_key.set()

    @log.catch
    @permission("tg_allowed")
    async def waiting_binance_secret_key(self, msg: Message,
                                         state: FSMContext, *args, **kwargs):
        """Обработчик кнопки pay\""""
        await state.finish()
        user = msg.from_user
        customer = await self.bi.get_customer(user.id)

        text = TextsManager.binance_api_recieved(customer['tg_profile']['language'])
        res = await self.bi.update_binance_secret_key(user.id, msg.text)
        await msg.delete()
        await self.bot.send_message(
            user.id,
            text
        )

    @log.catch
    @permission("tg_allowed")
    async def handle_pay(self, msg: Message,
                         state: FSMContext, *args, **kwargs):
        """Обработчик кнопки pay\""""

        user = msg.from_user

        subs = await self.bi.get_subscriptions()
        subs = [i for i in subs if i['name'].lower() != 'test']

        customer = await self.bi.get_customer(user.id)

        text = TextsManager.pay_select(customer['tg_profile']['language'])

        rm = KeyboardManager.pay_button(subs)

        await self.bot.send_message(
            user.id,
            text, reply_markup=rm
        )

    @log.catch
    @permission("tg_allowed", "payed")
    async def handle_webapp_response(self, message: Message,
                                     state: FSMContext, *args, **kwargs):
        user = message.from_user
        tg_profile = await self.bi.get_tg_profile(user.id)
        text_stop_monitoring = TextsManager.cancel_monitoring_button_text(tg_profile['language'])

        ikm_ws_signal = InlineKeyboardMarkup()
        btn_cancel_monitoring = KeyboardButton(
            text_stop_monitoring,
            callback_data="btn_cancel_monitoring"
        )
        ikm_ws_signal.add(
            btn_cancel_monitoring
        )

        webapp_data = json.loads(message.web_app_data.data)
        text = f"Webapp data: {webapp_data}"

        # ликвидность выводим один раз при запуске
        webapp_data_out_liq = []
        liq_currencies = []
        for i in webapp_data:
            if i[0].find('LQVD') > -1:
                liq_currencies.append(i)
                all_links = await self.bi.get_timeframe_links()

                for currency_link in all_links:
                    first_symbol = currency_link['currency_pair']["first"]['abbr']
                    second_symbol = currency_link['currency_pair']["last"]['abbr']
                    symbol_check = first_symbol + second_symbol
                    if symbol_check == i[0]:
                        link = currency_link['link']
                        if link:
                            try:
                                image = await self.cr.get_beta_crtimg(
                                    link
                                )
                                await self.bot.send_photo(
                                    user.id,
                                    photo=image,
                                    caption=f'{symbol_check} Liquidity Level',
                                    reply_markup=ikm_ws_signal, parse_mode='html'
                                )
                                break


                            except Exception as e:
                                self.log.exception(e)
                                continue
                        break
            else:
                webapp_data_out_liq.append(i)
        await message.reply(
            text,
            reply_markup=ikm_ws_signal
        )
        if len(webapp_data_out_liq) == 0:
            return
        self.log.debug(text)

        url_data = encrypt(json.dumps({
            "tg_uid": str(user.id),
        }))

        wss_url = f"{WSS_BOT_URL}/home"

        async with websockets.connect(wss_url) as websocket:
            self.websockets[user.id] = websocket
            self.log.debug(f"Подключение к вебсокету создано ({wss_url})")

            await self.BotState.monitoring.set()

            async with state.proxy() as state_data:
                state_data["keep_monitoring"] = True
                self.log.debug(state_data)

            try:
                data = {
                    "a": "hello",
                    "f": "bot",
                    "t": url_data,
                }
                message = json.dumps(data)
                await websocket.send(message)

                t = time()

                async for message in websocket:

                    # Проверка статуса мониторинга
                    async with state.proxy() as state_data:
                        if state_data.get("keep_monitoring", False) == False:
                            # Отмена мониторинга
                            break

                    # Обработка сообщения от вебсокет-сервера
                    msgdata = json.loads(message)

                    match msgdata:
                        case {"a": "hello", "s": "ok"}:
                            for item in webapp_data_out_liq:
                                data = {
                                    "a": "add_sub:all",
                                    "p": item,
                                    "t": url_data,
                                }
                                message = json.dumps(data)
                                await websocket.send(message)

                        case {"a": "rcms", "s": "ok", "p": [*items]}:

                            for item in items:

                                symbol = item.get("symbol")
                                tf = item.get("tf")
                                symbol_fs_sd = []
                                link = ''
                                # all_currencypairs = await self.bi.get_allcurrencypairs()
                                all_links = await self.bi.get_timeframe_links()
                                # ускорить этот цикл
                                for i in all_links:
                                    first_symbol = i['currency_pair']["first"]['abbr']
                                    second_symbol = i['currency_pair']["last"]['abbr']
                                    symbol_check = first_symbol + second_symbol
                                    if symbol_check == symbol and i['time_frame']['abbr'] == tf:
                                        link = i['link']
                                        symbol_fs_sd.append(first_symbol)
                                        symbol_fs_sd.append(second_symbol)
                                        break
                                if not symbol_fs_sd:
                                    all_currencypairs = await self.bi.get_allcurrencypairs()
                                    for i in all_currencypairs:
                                        first_symbol = i["first"]['abbr']
                                        second_symbol = i["last"]['abbr']
                                        symbol_check = first_symbol + second_symbol
                                        if symbol_check == symbol:
                                            symbol_fs_sd.append(first_symbol)
                                            symbol_fs_sd.append(second_symbol)
                                            break
                                default_idcs = [
                                    "BB",
                                    "RSI",
                                    "MACD",
                                    "EMA:12",
                                    "EMA:26",
                                ]
                                if link:
                                    try:
                                        image = await self.cr.get_beta_crtimg(
                                            link
                                        )


                                    except Exception as e:
                                        self.log.exception(e)
                                        continue
                                else:
                                    indis_dict = await self.bi.get_tf_indicators(tf)
                                    idc_for_tf = indis_dict['indicators']
                                    if len(idc_for_tf) > 0:
                                        default_idcs = idc_for_tf

                                    try:
                                        image = await self.cr.get_image(
                                            symbol=symbol,
                                            interval=tf,
                                            studies=default_idcs,
                                            height=500,
                                        )

                                    except Exception as e:
                                        self.log.exception(e)
                                        continue

                                symbol = item.get("symbol")
                                tf = item.get("tf")

                                # Get CryptoBubble info
                                symbol_cryptobubble_fs = symbol_fs_sd[0]
                                symbol_cryptobubble_sd = symbol_fs_sd[1]

                                # storage two symbols in dict
                                info_cryptobubble = {}
                                info_cryptobubble[symbol_cryptobubble_fs] = await self.cb.get_currancy(
                                    symbol_fs_sd[0])
                                info_cryptobubble[symbol_cryptobubble_sd] = await self.cb.get_currancy(
                                    symbol_fs_sd[1])

                                crypto_bubble_text = ''
                                for currency, performance in info_cryptobubble.items():
                                    if info_cryptobubble.get(currency, None):
                                        crypto_bubble_text += f'\n🚀 <b>{currency}</b> :\n'
                                        for k, v in performance.items():
                                            if k == 'day' or k == 'min5' or k == 'min15' or (currency == 'USDT' and (
                                                    k == 'year' or k == 'hour' or k == 'week' or k == 'month')):
                                                continue

                                            elif k == '24h':
                                                crypto_bubble_text += f"📶Volume 24h: <b>{v}$</b>\n"
                                                continue
                                            elif k == 'marketcap':
                                                crypto_bubble_text += f"⚠️{k.capitalize()}: <b>{v}$</b>\n"
                                                continue
                                            crypto_bubble_text += f"{k.capitalize()}: <b>{v}%</b>\n"

                                binance_orderbook_text = await self.bo.get_orderbook_text(symbol)
                                caption = f"📊 Символ: <b>{symbol} </b> Таймфрейм: <b>{tf}</b>\n\n" \
                                          f"〽️<b>Индикаторы</b> \n" \
                                          f'⚙️Cipher B:<b> {"{:.2f}".format(item["rcms"]["Market Cipher B"]["Plot_5"])}  ' \
                                          f'{"{:.2f}".format(item["rcms"]["Market Cipher B"]["wt2"])}  ' \
                                          f'{"{:.2f}".format(item["rcms"]["Market Cipher B"]["Plot_6"])}\n</b>' \
                                          f'⚙️Squeeze momentum:<b>{"{:.2f}".format(item["rcms"]["Squize Momentum"]["Plot"])} \n</b>' \
                                          f'⚙️Woldpack ID: <b>{"{:.2f}".format(item["rcms"]["Wolfpack Id"]["Plot_2"])}\n</b>' \
                                          f'⚙️Vumanchu cipher B: <b>{"{:.2f}".format(item["rcms"]["VuManChu Cipher B"]["Buy_Small_green_dot"])}\n</b>' \
                                          f'⚙️RSI:<b>{"{:.2f}".format(item["rcms"]["RSI"]["RSI"])}  {"{:.2f}".format(item["rcms"]["RSI"]["RSIbased_MA"])}\n</b>' \
                                          f'⚙️Fund master: <b>{"{:.2f}".format(item["rcms"]["Fund master"]["plotcandle_0_ohlc_high"])}\n\n</b>' \
                                          f'🫧🫧<a href="https://cryptobubbles.net">CRYPTO BUBBLES </a>: {crypto_bubble_text}\n\n' \
                                          f'🥃🥃<a href="https://www.binance.com/ru/futures/{symbol}">OrderBook </a>: \n{binance_orderbook_text}\n\n '

                                # Проверка статуса мониторинга
                                async with state.proxy() as state_data:
                                    if state_data.get("keep_monitoring", False) == False:
                                        # Отмена мониторинга
                                        break
                                try:
                                    await self.bot.send_photo(
                                        user.id,
                                        photo=image,
                                        caption=caption,
                                        reply_markup=ikm_ws_signal, parse_mode='html'
                                    )
                                except Exception as err:
                                    await self.bot.send_message(user.id, text=caption, reply_markup=ikm_ws_signal,
                                                                parse_mode='html', disable_web_page_preview=True)
                                    self.log.exception(err)

                    t = time()


            except websockets.ConnectionClosed:
                self.log.debug("Вебсокет соединение закрыто.")
                return
            except KeyboardInterrupt:
                return
            except Exception as e:
                self.log.exception(e)

        text = TextsManager.cancel_monitoring_reply_text(tg_profile['language'])

        self.log.debug("Мониторинг остановлен")
        await self.bot.send_message(user.id, text)
        await self.BotState.dep.set()

    async def stop_monitoring(self, user: User, state: FSMContext):
        async with state.proxy() as data:
            try:
                data["keep_monitoring"] = False
            except KeyError:
                pass

        if self.websockets.get(user.id) is not None:
            websocket = self.websockets.pop(user.id)
            await websocket.close()

    @log.catch
    async def callback_btn_cancel_monitoring(self, cq: CallbackQuery,
                                             state: FSMContext, *args, **kwargs):
        """Обработчик кнопки \"Остановить мониторинг\""""

        self.log.debug("Нажата кнопка \"Остановить мониторинг\"")

        user = cq.from_user

        await self.stop_monitoring(user, state)
        await self.init_menu(user, state, only_keyboard=True)

    @log.catch
    async def callback_btn_cancel(self, cq: CallbackQuery,
                                  state: FSMContext, *args, **kwargs):
        """Обработчик кнопки \"Отмена\""""

        self.log.debug("Нажата кнопка отмены")

        user = cq.from_user

        await state.finish()
        self.log.debug("Состояние BotState очищено")
        tg_profile = await self.bi.get_tg_profile(user.id)
        text = TextsManager.cancel_reply_text(tg_profile['language'])

        await self.bot.send_message(user.id, text)
        await self.resolve_init_restart(user, state)

    @log.catch
    @permission("tg_allowed")
    async def callback_btn_payment(self, cq: CallbackQuery,
                                   state: FSMContext, *args, **kwargs):
        """Обработчик кнопки \"Отмена\""""
        user = cq.from_user
        self.log.debug("Нажата кнопка оплаты")
        data_splited = cq.data.split('_')
        sub_name = data_splited[1]
        day = data_splited[2]
        price = data_splited[3]
        order_id = f"{user.id}S{day}"
        response_invoice = self.pm.create_invoice(float(price), order_id=order_id)
        kb = KeyboardManager.pay_link_button(response_invoice['pay_url'])
        await self.bot.send_message(user.id, f"Оплатите, нажав по кнопке снизу", reply_markup=kb)

    @log.catch
    @permission("tg_allowed")
    async def callback_btn_language(self, cq: CallbackQuery,
                                    state: FSMContext, *args, **kwargs):
        """Обработчик кнопки смены языка"""
        user = cq.from_user
        self.log.debug("Нажата кнопка смены языка")
        lang_code = cq.data.split('_')[1]
        if lang_code == 'ru':
            new_lang_name = 'russian'
        elif lang_code == 'spa':
            new_lang_name = 'spanish'
        elif lang_code == 'chi':
            new_lang_name = 'chinese'
        else:
            new_lang_name = 'english'
        customer = await self.bi.update_customer(user.id, tg_profile={'language': new_lang_name})
        text = TextsManager.change_lang_reply(customer["tg_profile"]['language'], new_lang_name)

        await self.bot.send_message(user.id, text)
        await self.resolve_init_restart(user, state)

    @log.catch
    @permission("tg_allowed")
    async def handle_stateless_input(self, message: Message, *args, **kwargs):
        """Обработчик пользовательского ввода без состояния"""
        user = message.from_user
        tg_profile = await self.bi.get_tg_profile(user.id)
        text = TextsManager.stateless_input_text(tg_profile['language'])

        self.log.debug(f"Пользователь {user.first_name} (id: {user.id}) ввел \"{message.text}\"")
        await message.reply(text)

    @log.catch
    def start(self):
        """Запуск бот сервиса. Регистрирует обработчики и запускает поллинг."""

        # Команды
        self.dp.register_message_handler(
            self.handle_cmd_start,
            commands=["start"],
            state="*"
        )

        self.dp.register_message_handler(
            self.handle_cmd_admin,
            commands=["admin"],
            state="*"
        )
        self.dp.register_message_handler(
            self.handle_pay,
            commands=["pay"],
            state="*"
        )

        # Webapp хэндлеры
        self.dp.register_message_handler(
            self.handle_webapp_response,
            content_types="web_app_data",
            state="*",
        )

        self.dp.register_message_handler(
            self.handle_btn_profile,
            lambda msg: msg.text.lower() == 'profile',
            state=[
                "*"
            ],
        )
        self.dp.register_message_handler(
            self.handle_btn_profile,
            lambda msg: msg.text.lower() == 'профиль',
            state=[
                "*"
            ],
        )
        self.dp.register_message_handler(
            self.handle_btn_profile,
            lambda msg: msg.text.lower() == 'perfil',
            state=[
                "*"
            ],
        )
        self.dp.register_message_handler(
            self.handle_btn_profile,
            lambda msg: msg.text.lower() == '轮廓',
            state=[
                "*"
            ],
        )
        self.dp.register_callback_query_handler(
            self.handle_connect_binance,
            lambda cq: cq.data.lower() == 'connect_binance',
            state=[
                "*"
            ],
        )
        self.dp.register_message_handler(
            self.waiting_binance_api_key,
            state=[
                self.BotState.binance_api_key,
            ],
        )
        self.dp.register_message_handler(
            self.waiting_binance_secret_key,
            state=[
                self.BotState.binance_secret_key,
            ],
        )
        self.dp.register_callback_query_handler(
            self.callback_btn_payment,
            lambda cq: cq.data.split('_')[0] == 'payment',
            state="*"
        )
        # Пользовательский ввод
        self.dp.register_message_handler(
            self.handle_stateless_input
        )
        # Колбэки
        self.dp.register_callback_query_handler(
            self.callback_btn_cancel,
            lambda cq: cq.data == 'btn_cancel',
            state="*"
        )
        self.dp.register_callback_query_handler(
            self.callback_btn_language,
            lambda cq: cq.data.split('_')[0] == 'lang',
            state="*"
        )
        self.dp.register_callback_query_handler(
            self.callback_btn_payment,
            lambda cq: cq.data.split('_')[0] == 'payment',
            state="*"
        )

        self.dp.register_callback_query_handler(
            self.callback_btn_cancel_monitoring,
            lambda cq: cq.data == 'btn_cancel_monitoring',
            state=self.BotState.monitoring
        )

        self.log.info("Запуск бот сервиса")
        executor.start_polling(self.dp, skip_updates=True)
