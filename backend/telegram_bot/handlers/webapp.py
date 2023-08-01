import json
from typing import Dict

import websockets
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from binanceOrderbook.requests import BinanceOrderbook
from chartimg.requests import ChartImgAPI
from cryptoBubbles.requests import CryptoBubbleAPI
from interface.backend import BackendInterface
from settings import WSS_BOT_URL
from utils import encrypt
from fluent.runtime import FluentLocalization

from .. import loggers
from ..ui import get_cancel_monitoring_kb

router = Router()


@loggers.telegram.catch
@router.message(F.web_app_data)
async def handle_webapp_response(
        message: Message,
        state: FSMContext,
        wsocket: Dict,
        backend_interface: BackendInterface,
        binance_orderbook: BinanceOrderbook,
        crypto_bubble: CryptoBubbleAPI,
        chart_img: ChartImgAPI,
        l10n: FluentLocalization
):
    user = message.from_user

    ikm_ws_signal = get_cancel_monitoring_kb(l10n)

    webapp_data = json.loads(message.web_app_data.data)
    text = f"Webapp data: {webapp_data}"

    # ликвидность выводим один раз при запуске
    webapp_data_out_liq = []
    liq_currencies = []
    for i in webapp_data:
        if i[0].find('LQVD') > -1:
            liq_currencies.append(i)
            all_links = await backend_interface.get_timeframe_links()

            for currency_link in all_links:
                first_symbol = currency_link['currency_pair']["first"]['abbr']
                second_symbol = currency_link['currency_pair']["last"]['abbr']
                symbol_check = first_symbol + second_symbol
                if symbol_check == i[0]:
                    link = currency_link['link']
                    if link:
                        try:
                            image = await chart_img.get_beta_crtimg(
                                link
                            )
                            await message.answer_photo(
                                photo=image,
                                caption=f'{symbol_check} Liquidity Level',
                                reply_markup=ikm_ws_signal, parse_mode='html'
                            )
                            break

                        except Exception as e:
                            loggers.telegram.exception(e)
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
    loggers.telegram.debug(text)

    url_data = encrypt(json.dumps({
        "tg_uid": str(user.id),
    }))

    wss_url = f"{WSS_BOT_URL}/home"
    async with websockets.connect(wss_url) as websocket:
        wsocket[user.id] = websocket
        loggers.telegram.debug(f"Подключение к вебсокету создано ({wss_url})")

        await state.set_state("monitoring")
        await state.update_data(keep_monitoring=True)

        try:
            data = {
                "a": "hello",
                "f": "bot",
                "t": url_data,
            }
            message = json.dumps(data)
            await websocket.send(message)

            async for message in websocket:

                # Проверка статуса мониторинга
                if not (await state.get_data()).get("keep_monitoring", False):
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
                            all_links = await backend_interface.get_timeframe_links()
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
                                all_currencypairs = await backend_interface.get_allcurrencypairs()
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
                                    image = await chart_img.get_beta_crtimg(
                                        link
                                    )

                                except Exception as e:
                                    loggers.telegram.exception(e)
                                    continue
                            else:
                                indis_dict = await backend_interface.get_tf_indicators(tf)
                                idc_for_tf = indis_dict['indicators']
                                if len(idc_for_tf) > 0:
                                    default_idcs = idc_for_tf

                                try:
                                    image = await chart_img.get_image(
                                        symbol=symbol,
                                        interval=tf,
                                        studies=default_idcs,
                                        height=500,
                                    )

                                except Exception as e:
                                    loggers.telegram.exception(e)
                                    continue

                            symbol = item.get("symbol")
                            tf = item.get("tf")

                            # Get CryptoBubble info
                            symbol_cryptobubble_fs = symbol_fs_sd[0]
                            symbol_cryptobubble_sd = symbol_fs_sd[1]

                            # storage two symbols in dict
                            info_cryptobubble = {
                                symbol_cryptobubble_fs: await crypto_bubble.get_currancy(
                                    symbol_fs_sd[0]
                                ),
                                symbol_cryptobubble_sd: await crypto_bubble.get_currancy(
                                    symbol_fs_sd[1]
                                )
                            }

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

                            binance_orderbook_text = await binance_orderbook.get_orderbook_text(symbol)
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

                            if not (await state.get_data()).get("keep_monitoring"):
                                break

                            try:
                                await message.answer_photo(
                                    user.id,
                                    photo=image,
                                    caption=caption,
                                    reply_markup=ikm_ws_signal, parse_mode='html'
                                )
                            except Exception as err:
                                await message.answer(user.id, text=caption, reply_markup=ikm_ws_signal,
                                                     parse_mode='html', disable_web_page_preview=True)
                                loggers.telegram.exception(err)

        except websockets.ConnectionClosed:
            loggers.telegram.debug("Вебсокет соединение закрыто.")
            return
        except KeyboardInterrupt:
            return
        except Exception as e:
            loggers.telegram.exception(e)

    loggers.telegram.debug("Мониторинг остановлен")
    await message.answer(l10n.format_value("canceled-monitoring"))
    await state.set_state("dep")
