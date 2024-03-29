import connexion
from connexion import NoContent
import datetime
import json
import logging
import logging.config
import pykafka
from pykafka import KafkaClient
import requests
import uuid
import yaml


def process_event(event, endpoint):
    trace_id = str(uuid.uuid4())
    event["trace_id"] = trace_id

    logger.debug(f"Received {endpoint} event with trace id {trace_id}")

    hosts = f"{app_config['events']['hostname']}:{str(app_config['events']['port'])}"
    client = KafkaClient(
        hosts=f"{str(app_config['events']['hostname'])}:{str(app_config['events']['port'])}",
        socket_timeout_ms=100000,
    )

    topic = client.topics[app_config["events"]["topic"]]

    producer = topic.get_sync_producer()

    pro_dict = {
        "type": endpoint,
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": event,
    }

    pro_dict_json = json.dumps(pro_dict)

    producer.produce(pro_dict_json.encode("utf-8"))

    logger.debug(f"PRODUCER::producing {event} event")
    logger.debug(f"The json string is {pro_dict_json}")

    return NoContent, 201


# Endpoints
def buy(body):
    process_event(body, "buy")
    return NoContent, 201


def sell(body):
    process_event(body, "sell")
    return NoContent, 201


def health():
    print("check finished")
    return NoContent, 200


app = connexion.FlaskApp(__name__, specification_dir="")

app.add_api(
    "openapi.yml",
    base_path="/receiver",
    strict_validation=True,
    validate_responses=True,
)
with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())


with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basic")

if __name__ == "__main__":
    app.run(port=8080)
