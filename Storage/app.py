import datetime
import json

import connexion
from connexion import NoContent
import swagger_ui_bundle

import mysql.connector
import pymysql
import yaml
import logging
import logging.config

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from buy import Buy
from sell import Sell

import pykafka
from pykafka import KafkaClient
from pykafka.common import OffsetType

import threading
from threading import Thread


with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    user = app_config["user"]
    password = app_config["password"]
    hostname = app_config["hostname"]
    port = app_config["port"]
    db = app_config["db"]

DB_ENGINE = create_engine(
    f"mysql+pymysql://{app_config['user']}:{app_config['password']}@{app_config['hostname']}:{app_config['port']}/{app_config['db']}"
)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def process_messages():
    hosts = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hosts)

    topic = client.topics[app_config["events"]["topic"]]

    messages = topic.get_simple_consumer(
        reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST
    )

    for msg in messages:
        msg_str = msg.value.decode("utf-8")
        logger.debug(f"{msg_str}")

        msg_dict = json.loads(msg_str)

        payload = msg_dict.get("payload")
        logger.debug(payload)

        msg_type = msg_dict.get("type")

        logger.debug(f"CONSUMER::storing buy event")
        logger.debug(f"msg objetc {msg}")

        if msg_type == "buy":
            buy(payload)
        else:
            sell(payload)

    messages.commit_offsets()


# Endpoints
def buy(body):
    session = DB_SESSION()

    b = Buy(
        body["buy_id"],
        body["item_name"],
        body["item_price"],
        body["buy_qty"],
        body["trace_id"],
    )

    session.add(b)
    session.commit()

    logger.debug(f"Stored buy event with trace id {b.trace_id}")

    return NoContent, 201


def get_buys(timestamp):
    session = DB_SESSION()

    data = []

    rows = session.query(Buy).filter(Buy.date_created >= timestamp)
    for row in rows:
        data.append(row.to_dict())

    return data, 200


def sell(body):
    session = DB_SESSION()

    s = Sell(
        body["sell_id"],
        body["item_name"],
        body["item_price"],
        body["sell_qty"],
        body["trace_id"],
    )

    session.add(s)
    session.commit()

    logger.debug(f"Stored sell event with trace id {s.trace_id}")

    return NoContent, 201


def get_sells(timestamp):
    session = DB_SESSION()

    data = []

    rows = session.query(Sell).filter(Sell.date_created >= timestamp)
    for row in rows:
        data.append(row.to_dict())

    return data, 200


def health():
    print("check finished")
    return 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api(
    "openapi.yml", base_path="/storage", strict_validation=True, validate_responses=True
)
with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basic")

if __name__ == "__main__":
    tl = Thread(target=process_messages)
    tl.daemon = True
    tl.start()
    app.run(port=8090)
