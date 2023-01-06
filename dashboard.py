from flask import Flask
import os
from rabbitmq import Rabbitmq
from dramatiq.common import dq_name, q_name, xq_name

base_url = os.environ.get("BASE_URL", "")
rabbit_user = os.environ.get("RABBIT_USER", "")
rabbit_pass = os.environ.get("RABBIT_PASS", "")
vhost = os.environ.get("VHOST", "")


broker = Rabbitmq(base_url, rabbit_user, rabbit_pass, vhost)

app = Flask(__name__)


@app.route("/api", methods=["GET"])
def main_page():
    return broker.get_all_queues()


@app.route("/api/<queue_name>", methods=["GET", "POST"])
def messages_of_queue(queue_name):
    if queue_name == dq_name(queue_name) or queue_name == xq_name(queue_name):
        return {"status": "please enter the current queue name"}
    return broker.get_messages_of_queue(queue_name)


@app.route("/api/<queue_name>/<message_id>", methods=["GET", "POST"])
def requeue_msg(queue_name, message_id):
    return broker.requeue_msg(queue_name, q_name(queue_name), message_id)


if __name__ == "__main__":
    DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
    app.run(debug=DEBUG)
