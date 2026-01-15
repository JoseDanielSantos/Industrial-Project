import logging
import sys

from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.transport import HttpTransport

LOGSTASH_HOST = "localhost"
LOGSTASH_PORT = 5044      # <<< PORTA NOVA
LOGSTASH_USER = "botas"
LOGSTASH_PASSWORD = "minha_senha_123"
INPUT_FILE = "sensor_data.txt"


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("sensor-logstash")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    transport = HttpTransport(
        host=LOGSTASH_HOST,
        port=LOGSTASH_PORT,
        timeout=5.0,
        ssl_enable=False,    # HTTP simples
        ssl_verify=False,

        # >>> auth básica para o Logstash <<<
        username=LOGSTASH_USER,
        password=LOGSTASH_PASSWORD
    )

    handler = AsynchronousLogstashHandler(
        host=LOGSTASH_HOST,
        port=LOGSTASH_PORT,
        transport=transport,
        database_path=None,
    )

    logger.addHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def main():
    logger = setup_logger()

    with open(INPUT_FILE, "r") as file:
        for line in file:
            if not line.strip():
                continue

            timestamp, temperature, humidity = line.strip().split(";")
            record = {
                "timestamp": timestamp,
                "temperature": float(temperature),
                "humidity": float(humidity),
            }

            logger.info("sensor_reading", extra=record)
            print(f"Sent: {record}")


if __name__ == "__main__":
    main()
