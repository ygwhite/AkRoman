import asyncio as aio
import json
from io import BytesIO

from loguru._logger import Logger

from utils.requests import BaseRequest


class ChartImgAPI:
    __slots__ = "baseurl", "token", "chart_type", "url_beta", "apiver", "token_beta", "log", "rh"

    def __init__(self,
                 baseurl: str,
                 token: str,
                 url_beta: str,
                 token_beta: str,
                 chart_type: str,
                 apiver: str,
                 request_handler: BaseRequest,
                 log: Logger,
                 ):

        self.baseurl = baseurl
        self.token = token
        self.url_beta = url_beta
        self.token_beta = token_beta
        self.chart_type = chart_type
        self.apiver = apiver
        self.rh = request_handler
        self.log = log

    @property
    def url(self):
        url = f"{self.baseurl}/{self.apiver}/tradingview/{self.chart_type}"
        return f"{url}?%(params)s&key={self.token}"

    async def get_image(self, symbol, interval="1m",
                        studies=[], height=300, session=None) -> BytesIO:
        interval = interval.lower()
        if interval.isdigit():
            interval = interval + 'm'
        elif interval == 'd':
            interval = '1d'
        elif interval == 'w':
            interval = '1w'
        params = "&".join(f"{k}={v}" for k, v in (
            ("symbol", symbol),
            ("interval", interval),
            *[("studies", s) for s in studies],
            ("height", height)
        ))

        url = self.url % {"params": params}

        try:
            response = await self.rh.request("get", url, session=session)

            image = BytesIO(response.content)
            image.name = 'chart.png'
            image.seek(0)

            return image
        except Exception as e:
            self.log.exception(e)
            return None

    async def get_beta_crtimg(self, link):
        url_req = self.url_beta + link
        try:
            payload = json.dumps({
                "width": 1920,
                "height": 1080
            })
            headers = {
                'x-api-key': f'{self.token_beta}',
                'content-type': 'application/json'
            }
            response = await self.rh.request("post", url_req, payload, headers)

            image = BytesIO(response.content)
            image.name = 'chart.png'
            image.seek(0)

            return image
        except Exception as e:
            self.log.exception(e)
            return None

    async def get_many_images(self, req_items, loop=None) -> list[BytesIO]:
        if loop is None:
            loop = aio.get_event_loop()

        tasks = set()

        async with self.rh.new_session() as sess:
            for symbol, tf, studies, height in req_items:
                task = loop.create_task(
                    self.get_image(
                        symbol=symbol,
                        interval=tf,
                        studies=studies,
                        height=height,
                        session=sess,
                    )
                )
                tasks.add(task)

            images = await aio.gather(*tasks)

        return images
