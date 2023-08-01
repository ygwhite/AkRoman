import json
import time
import datetime as dt
import asyncio as aio
from ssl import SSLContext
from copy import deepcopy
from collections import defaultdict
from itertools import groupby

import websockets
from websockets.connection import Connection
from websockets.exceptions import ConnectionClosed
from loguru._logger import Logger
from TradingViewApi.requests import TradingViewApi
from interface.backend import BackendInterface
from tradingview_uapi.scan import TVUAPI
from tradingview_uapi.calc import calculate
from utils import decrypt


class WSServer:
    __slots__ = (
        "host", "port", "ssl",  # подключение
        "bi", "tva",  # интерфейсы
        "interval",  # время которое дается на цикл загрузки/рассылки
        "conns",  # состояния подключений
        "subs_rd", "subs2_rd",  # последние данные
        "loop", "lock",  # asyncio
        "taskq", "qlimit",  # tasks
        "log"
    )

    class RecentData:
        __slots__ = "groups", "idcs", "rcms",

        def __init__(self):
            """
            Хранилище для:
            - последних сгруппированных символов с таймфреймами
            - последих загруженных индикаторов
            - последних отправленных рекомендаций
            """

            self.groups = defaultdict(list)
            self.idcs = dict()
            self.rcms = dict()

    def __init__(self,
                 host: str,
                 port: str,
                 ssl_context: SSLContext | None,
                 interval: int,
                 tva: TradingViewApi,
                 bi: BackendInterface,
                 qlimit: int,
                 log: Logger):

        self.host = host
        self.port = port
        self.ssl = ssl_context
        self.interval = interval
        self.tva = tva
        self.subs_rd = self.RecentData()
        self.subs2_rd = self.RecentData()
        self.bi = bi
        self.conns = dict()
        self.loop = aio.get_event_loop()
        self.lock = aio.Lock()
        self.taskq = aio.Queue()
        self.qlimit = qlimit
        self.log = log

    async def task_accept_connection(self, conn: Connection, token: str) -> None:
        """Регистрация нового подключения"""

        if self.conns.get(conn) is None:
            token_data = json.loads(decrypt(token))
            tg_uid = token_data.get("tg_uid")

            if tg_uid is None:
                return

            customer = await self.bi.get_customer(tg_uid)
            if customer.get("tg_profile", {}).get("is_allowed", False) == True:
                self.conns[conn] = {"tg_uid": tg_uid}

        if self.is_registered(conn, token) == False:
            return

        conn_sign = f"path: /home, tg_uid: {tg_uid}"
        self.log.debug(f"Connection accepted ({conn_sign})")

        message = json.dumps({"a": "hello", "s": "ok"})
        await self.send_message(conn, message)

    async def task_add_sub(self, conn: Connection, token: str,
                           symbol: str, tf: str, conn_sign: str) -> None:
        """Регистрация новой подписки для данного соединения"""

        if self.is_registered(conn, token) == False:
            return

        self.log.debug(f"Обновление: {symbol}, {tf} ({conn_sign})")

        if symbol is None or tf is None:
            return

        item = symbol, tf

        async with self.lock:
            subs = deepcopy(self.conns.get(conn, {}).get("subs", {}))

        # Обнуление последних рекомендаций
        subs[item] = {"last_rcms": {}}

        async with self.lock:
            try:
                self.conns[conn]["subs"] = subs
            except Exception as e:
                self.log.exception(e)

        message = json.dumps({"a": "add_sub:all", "s": "ok"})
        await self.send_message(conn, message)

        # Отправить рекомендацию, если таковая уже имеется
        await self.send_rcms(conn)

    async def task_clear_subs(self, conn: Connection, token: str) -> None:
        """Удаление всех подписок для данного соединения"""
        async with self.lock:
            try:
                self.conns[conn]["subs"] = {}
            except Exception as e:
                self.log.exception(e)

        message = json.dumps({"a": "clear_subs", "s": "ok"})
        await self.send_message(conn, message)

    async def task_conn_close(self, conn: Connection) -> None:
        """Закрытие соединения"""

        if self.conns.get(conn) is None:
            return

        tg_uid = self.conns[conn].get("tg_uid")
        if tg_uid is None:
            conn_sign = f"conn_id: {conn.id}"
        else:
            conn_sign = f"tg_uid: {tg_uid}"

        self.log.debug(f"Соединение закрыто ({conn_sign})")

        async with self.lock:
            # Удаление состояния
            self.conns.pop(conn)

    async def handle_home_conn_message(self, conn: Connection,
                                       message: str, conn_sign: str) -> None:
        """Обработка нового сообщения для адреса '/home'"""

        self.log.debug(f"Входящее сообщение: {message} ({conn_sign})")

        msgdata = json.loads(message)

        match msgdata:
            case {"a": "hello", "f": "webapp" | "bot", "t": token}:

                await self.taskq.put(
                    self.loop.create_task(
                        self.task_accept_connection(conn, token)
                    )
                )

            case {"a": "add_sub:all", "p": [symbol, tf], "t": token}:

                await self.taskq.put(
                    self.loop.create_task(
                        self.task_add_sub(conn, token, symbol, tf, conn_sign)
                    )
                )

            case {"a": "clear_subs", "t": token}:

                await self.taskq.put(
                    self.loop.create_task(
                        self.task_clear_subs(conn, token)
                    )
                )

            case _:
                self.log.debug(f"Неожиданный паттерн: {msgdata}")
                pass

    async def handle_new_connection(self, conn: Connection, path: str) -> None:
        """Обработчик новых подключений"""

        self.log.debug(f"Соединение открыто. (path: {path}, conn_id: {conn.id})")

        try:
            match path:
                case "/home":
                    # -- Обработка входящих сообщений по адресу /home --

                    # подпись для логов
                    conn_sign = f"path: /home, conn_id: {conn.id}"

                    async for message in conn:
                        await self.handle_home_conn_message(conn, message, conn_sign)

                case _:
                    pass

        except websockets.exceptions.ConnectionClosed:
            return

        except KeyboardInterrupt:
            return

        except Exception as e:
            self.log.exception(e)

        finally:
            await self.taskq.put(
                self.loop.create_task(
                    self.task_conn_close(conn)
                )
            )

    def is_registered(self, conn: Connection, token: str) -> bool:
        """Проверка санкционированности подключения"""

        token_data = json.loads(decrypt(token))

        tg_uid = token_data.get("tg_uid")
        if tg_uid is None:
            return False

        state = self.conns.get(conn)
        if state is None:
            return False

        return state.get("tg_uid") == tg_uid

    async def update_symbol_groups(self) -> None:
        """
        Группировка символов по таймфреймам для оптимизации запросов к серверам 
        tradingview
        """
        total_items = set()  # set([(symbol1, tf1), (symbol2, tf2)])
        req_groups = defaultdict(list)

        async with self.lock:
            states = deepcopy(tuple(self.conns.values()))

        for state in states:
            conn_items = set(state.get("subs", dict()).keys())
            total_items.update(conn_items)

        comparator = lambda x: x[0]
        sorted_items = sorted(total_items, key=comparator)
        for key, valiter in groupby(sorted_items, key=comparator):
            key_groups = defaultdict(set)
            for key, val in valiter:
                key_groups[key].add(val)

            for key, val in key_groups.items():
                req_groups[tuple(sorted(val))].append(key)

        async with self.lock:
            self.subs_rd.groups = req_groups

        self.log.debug(f"Updated request groups {self.subs_rd.groups}")

    async def send_message(self, conn: Connection, message: str) -> None:
        """Отправка сообщения"""

        try:
            await conn.send(message)
            self.log.debug(f"Отправка сообщения: {message}")
        except ConnectionClosed:
            return
        except Exception as e:
            self.log.exception(e)

    async def send_rcms(self, conn: Connection) -> None:
        """Рассылка загруженных рекомендаций"""

        async with self.lock:
            # копирование состояния, так как оно может асинхронно меняться
            subs = deepcopy(self.conns.get(conn, {}).get("subs", {}))

        items = []

        # Отбор новых рекомендаций. Старые игнорируются
        for key in subs.keys():
            symbol, tf = key
            rcms = self.subs_rd.rcms.get(symbol, {}).get(tf, {})
            if not subs[key].get("last_rcms") and rcms:
                subs[key]["last_rcms"] = rcms
                p_item = {"symbol": symbol, "tf": tf, "rcms": rcms}
                items.append(p_item)
            # Если рекомендации старые -- идем к следующим
            if (subs[key].get("last_rcms") and rcms) and (
                    subs[key].get("last_rcms")['RSI']["RSI"] >
                    rcms['RSI']["RSI"] + 5 or
                    subs[key].get("last_rcms")['RSI']["RSI"] <
                    rcms['RSI']["RSI"] - 5):

                p_item = {"symbol": symbol, "tf": tf, "rcms": rcms}
                items.append(p_item)

                # Локальное обновление старых рекомендаций
                subs[key]["last_rcms"] = rcms
            else:
                continue

        if len(items) == 0:
            return

        msg_data = {
            "a": "rcms",
            "s": "ok",
            "p": items
        }

        # Обновление состояния
        async with self.lock:
            try:
                self.conns[conn]["subs"] = subs
            except Exception as e:
                self.log.exception(e)
        # Отправка отобранных рекомендаций
        message = json.dumps(msg_data)
        await self.send_message(conn, message)

    async def execution_loop(self) -> None:
        """ Основной исполняемый цикл
        Выполняет:
        - n задач из очереди taskq; n = qlimit
        - группирует символы из всех подключений
        - скачивает индикаторы для этих групп
        - вычисляет рекомендации по индикаторам
        - рассылает результаты вычислений подписчикам
        Если все задачи исполнились раньше значения interval, 
        цикл будет спать оставшееся время.
        """

        while True:
            t = dt.datetime.now()

            # Выполнение задач ожидающих в очереди
            c = 0
            while self.taskq.empty() == False and c < self.qlimit:
                task = await self.taskq.get()
                await task
                c += 1

            # Группировка символов с таймфреймами
            await self.update_symbol_groups()

            if len(self.conns) > 0 and len(self.subs_rd.groups) > 0:

                self.log.debug(f"Загрузка индикаторов и расчет рекомендаций")

                async with self.lock:
                    req_groups = deepcopy(self.subs_rd.groups)

                data_idcs = {}
                data_rcms = {}

                # Сбор тех.идикаторов для групп символов
                try:
                    idcs_groups_dict = await self.tva.get_many_ids(req_groups)

                    # idcs_groups_list = await self.tvuapi.post_many_idcs(
                    #     req_groups, loop=self.loop,
                    # )

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    idcs_groups_dict = []
                    self.log.exception(e)
                for symbol in idcs_groups_dict:
                    if data_idcs.get(symbol) is None:
                        data_idcs[symbol] = {}

                    if data_rcms.get(symbol) is None:
                        data_rcms[symbol] = {}

                    for tf, idcs in idcs_groups_dict[symbol].items():
                        # Объединение индикаторов в один словарь data.idcs
                        data_idcs[symbol][tf] = idcs
                        # Вычисление рекомендаций и объединение их в data.rcms
                        data_rcms[symbol][tf] = idcs

                async with self.lock:
                    self.subs_rd.idcs = data_idcs
                    self.subs_rd.rcms = data_rcms

                # Рассылка рекомендаций подписчикам
                if len(self.subs_rd.rcms) > 0:

                    self.log.debug("Рассылка рекомендаций")

                    async with self.lock:
                        conns = tuple(self.conns.keys())

                    for conn in conns:
                        await self.send_rcms(conn)

            self.log.debug(f"Connections: {tuple(self.conns.keys())}")
            self.log.debug(f"Req. groups: {self.subs_rd.groups}")
            self.log.debug(f"Indicators: {self.subs_rd.idcs}")
            self.log.debug(f"Recomendations: {self.subs_rd.rcms}")

            td = dt.datetime.now() - t
            ts = td.seconds + td.microseconds / 1000000
            # Если загрузка/рассылка закончилась раньше значения interval
            # цикл будет спать оставшееся время
            self.log.debug(f"Time to sleep {self.interval - ts} seconds")
            if self.interval > ts:
                await aio.sleep(self.interval - ts)

    def reset_server(self) -> None:
        """Перезагрузка состояния сервера"""
        self.log.debug("Перезагрузка состояния сервера")

        conns = tuple(self.conns.keys())

        for conn in conns:
            try:
                self.loop.run_until_complete(conn.close())
            except:
                pass

        self.conns = dict()
        self.subs_rd = self.RecentData()

        self.loop.close()
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        self.loop = loop

    def start(self) -> None:
        """Запуск websocket сервера"""
        self.log.debug("Запуск websocket сервера")

        while True:
            task_conn = websockets.serve(
                self.handle_new_connection,
                self.host,
                self.port,
                ssl=self.ssl
            )
            task_loop = self.loop.create_task(self.execution_loop())

            try:
                gather_promise = aio.gather(
                    task_conn,
                    task_loop,
                )

                self.loop.run_until_complete(gather_promise)
                self.loop.run_forever()

            except KeyboardInterrupt:
                break

            except OSError as e:
                self.log.error(f"OSError: {e}")

            except Exception as e:
                self.log.exception(e)

            finally:
                self.reset_server()

            time.sleep(10)
