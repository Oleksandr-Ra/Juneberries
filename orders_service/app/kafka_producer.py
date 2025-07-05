# /common/kafka_producer.py

import json
import logging
from kafka import KafkaProducer

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

 
class Producer:
    """
    Class for sending messages to Kafka.
    """
    def __init__(self):
        self.producer = None
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.kafka_broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=10000,  # 10 second
                retries=5
            )
            logger.info('✅ Kafka Producer initialized successfully.')
        except Exception as e:
            logger.error(f'🛑 Failed to initialize Kafka Producer: {e}')

    def send_message(self, topic: str, message: dict):
        """
        Sends a message to the specified topic.
        """
        if not self.producer:
            logger.error('🛑 Producer is not initialized. Cannot send message.')
            return

        try:
            logger.info(f'Sending message to topic "{topic}": {message}')
            self.producer.send(topic=topic, value=message)
        except Exception as e:
            logger.error(f'Error sending message to Kafka: {e}')

    def close(self):
        """
        Closes the connection to Kafka.
        """
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info('❌ Kafka Producer closed.')


kafka_producer = Producer()
