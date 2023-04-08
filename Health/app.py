import connexion
import json
import logging
import logging.config
import requests
import yaml
from flask_cors import CORS

statuses = {"receiver": "", "storage": "", "processing": ""}
services = {
    "receiver": "http://34.130.96.245/receiver/health",
    "storage": "http://34.130.96.245/storage/health",
    "processing": "http://34.130.96.245/processing/health",
}


def check():
    for service, url in services.items():
        try:
            res = requests.get(url)
            if res.status_code == 200:
                statuses[service] = "Running"
            else:
                statuses[service] = "Down"
        except requests.exceptions.RequestException:
            statuses[service] = "Down"

    return statuses


app = connexion.FlaskApp(__name__, specification_dir="")

# if you are deploying this to your VM, make sure to add base_path="/health" to the add_api method (and update your NGINX config to proxy requests to the health service)
app.add_api(
    "openapi.yml", base_path="/health", strict_validation=True, validate_responses=True
)
CORS(app.app)

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basic")

if __name__ == "__main__":
    app.run(port=8110)
