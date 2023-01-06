from flask import Flask
import os
from rabbitmq import Rabbitmq
from dramatiq.common import dq_name, q_name, xq_name
import config

conf = config.Config()

BASE_URL = conf.base_url
RABBIT_USER = conf.rabbit_user
RABBIT_PASS = conf.rabbit_pass
VHOST = conf.vhost
DEBUG = conf.debug
HOST = conf.host
PORT = conf.port


broker = Rabbitmq(BASE_URL, RABBIT_USER, RABBIT_PASS, VHOST, HOST, PORT)

app = Flask(__name__)


@app.route("/api", methods=["GET"])
def main_page():
    return broker.get_all_queues()


@app.route("/api/<queue_name>", methods=["POST"])
def messages_of_queue(queue_name):
    if queue_name == dq_name(queue_name) or queue_name == xq_name(queue_name):
        return {"Status": "Please enter the current queue name"}
    return broker.get_messages_of_queue(queue_name)


@app.route("/api/requeue/<queue_name>/<message_id>", methods=["POST"])
def requeue_msg(queue_name, message_id):
    if queue_name == q_name(queue_name):
        return {"Status": "Please enter a delay or dead queue name"}
    return broker.requeue_msg(queue_name, q_name(queue_name), message_id)


@app.route("/api/delete/<queue_name>/<message_id>", methods=["DELETE"])
def delete_msg(queue_name, message_id):
    return broker.delete_msg(queue_name, message_id)


if __name__ == "__main__":
    app.run(debug=DEBUG)
