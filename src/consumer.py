import json
import sys
import django
import os
import pika

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()


from producer import EventType, EXCHANGE_NAME
from core.consume import create_grant_to_proccess
from core.consume import update_application_status_after_creating_grant


class Consumer:
    binded: bool = False

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.environ.get("RABBITMQ_HOST", "localhost"),
                port=os.environ.get("RABBITMQ_PORT", 5672),
            )
        )
        self.channel = self.connection.channel()
        if not self.binded:
            self.channel.queue_bind(
                queue=EventType.APPLICATION_APPROVED, exchange=EXCHANGE_NAME
            )
            self.channel.queue_bind(
                queue=EventType.GRANT_ACTIVATED, exchange=EXCHANGE_NAME
            )

    def callback_on_application_approved_status(
        self,
        ch: pika.BlockingConnection,
        method: pika.spec.Basic,
        properties,
        body: bytes,
    ):
        print(" [x] Received %r" % json.loads(body))
        body = json.loads(body)
        create_grant_to_proccess(
            user_id=body["user_id"],
            resource_id=body["resource_id"],
            application_id=body["application_id"],
        )

    def callback_on_grant_activated(
        self,
        ch: pika.BlockingConnection,
        method: pika.spec.Basic,
        properties,
        body: bytes,
    ):
        body = json.loads(body)
        print("callback_on_grant_activated", body)
        update_application_status_after_creating_grant(
            application_id=body["application_id"]
        )

    def run(self):
        self.channel.basic_consume(
            queue=EventType.APPLICATION_APPROVED,
            on_message_callback=self.callback_on_application_approved_status,
            auto_ack=True,
        )
        self.channel.basic_consume(
            queue=EventType.GRANT_ACTIVATED,
            on_message_callback=self.callback_on_grant_activated,
            auto_ack=True,
        )
        self.channel.start_consuming()


def main():
    consumer = Consumer()
    print(" [*] Waiting for messages. To exit press CTRL+C")
    consumer.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
