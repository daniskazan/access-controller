import json
from enum import Enum

from django.conf import settings

import pika
from pika.exchange_type import ExchangeType

EXCHANGE_NAME = "applicationsEvents"


class EventType(str, Enum):
    APPLICATION_APPROVED = "applications.approved"
    APPLICATION_RESOLVED = "applications.resolved"


class Producer:
    binded: bool = False

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_SETTINGS["HOST"],
                port=settings.RABBITMQ_SETTINGS["PORT"],
            )
        )
        self.channel = self.connection.channel()
        if not self.binded:
            self.channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=ExchangeType.direct)
            self.channel.queue_declare(queue=EventType.APPLICATION_APPROVED)
            self.channel.queue_declare(queue=EventType.APPLICATION_RESOLVED)
            self.channel.queue_bind(
                queue=EventType.APPLICATION_APPROVED, exchange=EXCHANGE_NAME
            )
            self.channel.queue_bind(
                queue=EventType.APPLICATION_RESOLVED, exchange=EXCHANGE_NAME
            )
            self.channel.close()

    def publish(self, *, routing_key: EventType, message: dict, exchange=EXCHANGE_NAME):
        channel = self.connection.channel()
        channel.basic_publish(
            exchange=exchange, routing_key=routing_key, body=json.dumps(message)
        )


producer = Producer()
