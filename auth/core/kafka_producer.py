import json
import logging
from typing import Any

from confluent_kafka import (KafkaError, KafkaException, Producer,
                             KafkaTimeoutError, KafkaConnectionError)

from auth.core.config import settings, setup_logging

setup_logging()


class KafkaProducer:
    def __init__(self):
        self.producer = Producer(
            {"bootstrap.servers": settings.kafka.kafka_bootstrap_servers}
        )

    def send_event(self, topic: str, key: str, value: dict):
        try:
            self.producer.produce(
                topic, key=key, value=json.dumps(value), callback=self.delivery_report
            )
            self.producer.flush()
        except KafkaTimeoutError:
            raise exceptions.KafkaTimeoutError
        except KafkaConnectionError:
            raise exceptions.KafkaConnectionError
        except KafkaError:
            raise exceptions.KafkaError

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def get_kafka_producer() -> KafkaProducer:
    return KafkaProducer()
