import json
import logging
import os
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record):
        log_record = {
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z',
            'level': record.levelname,
            'service': self.service_name,
            'message': record.getMessage()
        }
        return json.dumps(log_record)


def setup_logger(service_name: str = 'service_name'):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_dir = './logs'
    os.makedirs(log_dir, exist_ok=True)
    handler = logging.FileHandler(f'{log_dir}/{service_name}.log')
    handler.setFormatter(JsonFormatter(service_name))

    logger.handlers = [handler]
    return logger
