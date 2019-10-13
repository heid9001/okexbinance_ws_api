from .handlers import amq_handler
from .api import BinanceApi, OkexApi
import asyncio, os, sys
import logging

def run_bot(cls):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cls().channel())

def run_sub():
    amq_handler()

if __name__ == "__main__":
    logging.getLogger("pika").setLevel(logging.NOTSET)
    action = ''
    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        action = os.environ.get("NODE_TYPE", "none")
    {
        'binance':  lambda: run_bot(BinanceApi),
        'okex':     lambda: run_bot(OkexApi),
        'sub':      lambda: run_sub()
    }[action]()
