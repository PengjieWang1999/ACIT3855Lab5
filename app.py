from connexion import NoContent
import connexion
from pykafka import KafkaClient
import yaml
import json
from flask_cors import CORS, cross_origin
import logging
import logging.config

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


def get_hd_offset(offset):
    client = KafkaClient(hosts=app_config['datastore']['server'] + ':' + str(app_config['datastore']['port']))
    topic = client.topics[app_config['datastore']['topic']]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)
    msg_list = []
    for msg in consumer:
        print(msg)
        msg_str = msg.value.decode('utf-8')
        msg_dict = json.loads(msg_str)
        if msg_dict["type"] == "hd":
            msg_list.append(msg_dict['payload'])
    print(msg_list)
    if len(msg_list) >= offset:
        response = msg_list[offset]
    else:
        response = "Not in Range"

    logger.debug("Humidity Message List: " + str(msg_list))

    return response, 200


def get_tp_offset(offset):
    client = KafkaClient(hosts=app_config['datastore']['server'] + ':' + str(app_config['datastore']['port']))
    topic = client.topics[app_config['datastore']['topic']]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)
    msg_list = []
    for msg in consumer:
        print(msg)
        msg_str = msg.value.decode('utf-8')
        msg_dict = json.loads(msg_str)
        if msg_dict["type"] == "tp":
            msg_list.append(msg_dict['payload'])
    print(msg_list)
    if len(msg_list) >= offset:
        response = msg_list[offset]
    else:
        response = "Not in Range"

    logger.debug("Temperature Message List: " + str(msg_list))

    return response, 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml")

if __name__ == "__main__":
    # run our standalone event server
    app.run(port=8200)
