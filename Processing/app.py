import connexion
from connexion import NoContent
import datetime
import json
import logging
import logging.config
import requests
import yaml
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats
from flask_cors import CORS


DB_ENGINE = create_engine("sqlite:///stats.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_latest_stats():
    session = DB_SESSION()

    result = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    data = result.to_dict()

    return data


def populate_stats():
    session = DB_SESSION()

    data = get_latest_stats()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    last_updated = data["last_updated"]
    buy_events = requests.get(
        f"http://34.130.96.245/storage/buy?timestamp={last_updated}"
    )
    buy_events = buy_events.json()
    print(buy_events)
    for b_event in buy_events:
        if b_event["item_price"] > data["max_buy_price"]:
            data["max_buy_price"] = b_event["item_price"]
        data["num_buys"] += b_event["buy_qty"]

    sell_events = requests.get(
        f"http://34.130.96.245/storage/sell?timestamp={last_updated}"
    )
    sell_events = sell_events.json()
    for s_event in sell_events:
        if s_event["item_price"] > data["max_sell_price"]:
            data["max_sell_price"] = s_event["item_price"]
        data["num_sells"] += s_event["sell_qty"]

    data["last_updated"] = timestamp

    stats = Stats(**data)

    session.add(stats)
    session.commit()
    session.close()

    return NoContent, 201


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, "interval", seconds=app_config["period"])
    sched.start()


def health():
    print("check finished")
    return 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api(
    "openapi.yml",
    base_path="/processing",
    strict_validation=True,
    validate_responses=True,
)
CORS(app.app)

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger("basic")

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
