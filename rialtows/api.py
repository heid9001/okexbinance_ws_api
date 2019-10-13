from .dto import OkexDto, BinanceDto
import aiohttp
from yarl import URL
import json, zlib, pika, pickle, os


def amq_pub(dto):
    # create connection
    con = pika.BlockingConnection(pika.ConnectionParameters(os.environ.get("QHOST"), port=5672))
    # create threadsafe channel
    channel = con.channel()
    # assign queue
    channel.queue_declare(queue=os.environ.get("QNAME"))
    # publish message (routing_key - это имя роута)

    channel.basic_publish(
        exchange='',
        routing_key=os.environ.get("QNAME"),
        body=pickle.dumps(dto)
    )
    con.close()


class Client:

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def create_conn(self):
        return await (await self.get_session())\
            .ws_connect(self.create_url())

    async def __aenter__(self):
        self.connection = await self.create_conn()
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()

    def create_url(self, **kwargs):
        self.url_params.update(kwargs)
        return URL.build(**self.url_params)


class BaseApi:

    def __init__(self, **kwargs):
        self.url_params = kwargs
        self.session = None
        self.connection = None

    def publish_all(self, msgs, dtocls, cb=None):
        for msg in msgs:
            if cb is not None and cb(msg): continue
            dto = dtocls(msg)
            amq_pub(dto)

    async def __call__(self, method, **params):
        async with self as conn:
            if callable(method): await method(conn, **params)
            else: await (getattr(self, "call_"+method))(conn, **params)

    async def close(self):
        await self.session.close()


class OkexApi(BaseApi, Client):

    def unpack(self, msg):
        data = self._inflate(msg)
        return json.loads(data)

    # https://github.com/okcoin-okex/API-docs-OKEx.com/tree/master/demo
    def _inflate(self, data):
        decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
        )
        inflated = decompress.decompress(data)
        inflated += decompress.flush()
        return inflated

    def __init__(self):
        super().__init__(
            scheme='wss',
            host='real.okex.com',
            port=8443,
            path='/ws/v3',
        )

    async def publish(self, msg):
        data = self.unpack(msg.data)
        if 'data' not in data: return
        data = data['data']
        self.publish_all(data, dtocls=OkexDto)

    async def channel(self):
        while True:
            try:
                await self('ticker')
            except Exception as e: pass

    async def call_ticker(self, conn):
        await conn.send_json({
            'op':'subscribe',
            'args':['spot/ticker:ETH-USDT']
        })
        async for msg in conn:
            await self.publish(msg)


class BinanceApi(BaseApi, Client):

    def unpack(self, msg):
        return json.loads(msg)

    def __init__(self):
        super().__init__(
            scheme='wss',
            host='stream.binance.com',
            port=9443,
            path=''
        )
        self.symbol = None

    async def publish(self, msg):
        data = self.unpack(msg.data)
        data = filter(lambda row: row['s'] == self.symbol, data)
        self.publish_all(data, dtocls=BinanceDto)

    async def channel(self):
        self.symbol = "ETHUSDT"
        while True:
            try:
                self.create_url(path="/ws/!ticker@arr")
                await self('ticker')
            except Exception as e: pass

    async def call_ticker(self, conn):
        async for msg in conn:
            await self.publish(msg)