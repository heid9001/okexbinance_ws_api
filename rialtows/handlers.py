from .core import Registry
import pika, pickle
from datetime import datetime
import os


def amq_handler():

    regist = {
        'binance': {
            'bids': Registry(target="bid"),
            'ask': Registry(target="ask")
        },
        'okex': {
            'bids': Registry(target="bid"),
            'ask': Registry(target="ask")
        }
    }

    def avg(registry):
        bid = registry['bids'].get_after(0, cb=min)
        ask = registry['ask'].get_after(0, cb=max)
        return (bid + ask) / 2

    # обработка сообщений подписчика
    def handler(ch, method, properties, body):
        dto = pickle.loads(body)
        registry = regist[dto.name]
        registry['bids'].add(dto.date, dto)
        registry['ask'].add(dto.date, dto)

        print("%s %s %.2f"% (datetime.now(), dto.name, avg(registry)))

    # создание подключения к rabbitmq/tcp
    con = pika.BlockingConnection(pika.ConnectionParameters(os.environ.get("QHOST"), port=5672))
    # создание виртуального подключения
    channel = con.channel()
    # создание и/или подключение к очереди сообщений
    channel.queue_declare(queue=os.environ.get("QNAME"))
    # настройка получения сообщений
    channel.basic_consume(
        queue=os.environ.get("QNAME"),
        auto_ack=True,
        on_message_callback=handler
    )
    # слушатель подключенией
    channel.start_consuming()
