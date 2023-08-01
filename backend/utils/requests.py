from httpx import AsyncClient


class RotationManager:
    __slots__ = "idx", "datalist"

    def __init__(self, datalist: list):
        self.idx = 0
        self.datalist = datalist

    def next(self):
        data = self.datalist[self.idx]
        self.idx = (self.idx + 1) % len(self.datalist)
        return data


class IdManager:
    __slots__ = "headers", "uaman", "ua", "proxman", "proxy"

    def __init__(self,
                 headers: dict[str, str] = dict(),
                 uaman: RotationManager = None,
                 proxman: RotationManager = None):

        self.headers = headers
        self.uaman = uaman
        self.proxman = proxman
        self.new_identity()

    def new_identity(self):
        if isinstance(self.uaman, RotationManager):
            self.ua = self.uaman.next()
            self.headers["User-Agent"] = self.ua
        else:
            self.ua = None

        if isinstance(self.proxman, RotationManager):
            self.proxy = self.proxman.next()
        else:
            self.proxy = None
        # TODO add tor stem support


class BaseRequest:
    __slots__ = "idm", "timeout"

    def __init__(self,
                 idmanager: IdManager = IdManager(),
                 timeout: int = 0):

        self.idm = idmanager
        self.timeout = timeout

    def new_session(self):
        return AsyncClient(
            headers=self.idm.headers,
            proxies=self.idm.proxy,
            timeout=self.timeout,
            verify=False
        )

    async def request(self,
                      method: str,
                      url: str,
                      json: str | None = None,
                      headers: dict | None = None,
                      session: AsyncClient | None = None):

        if session is None:
            __session = self.new_session()
        else:
            __session = session

        response = None

        try:
            match method:
                case "get":
                    response = await __session.get(url)
                case "post":
                    response = await __session.post(url, data=json, headers=headers)
                case _:
                    raise Exception("Unsupported type of request")
        finally:
            if session is None:
                await __session.aclose()

        return response
