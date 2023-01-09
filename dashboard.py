from flask import render_template, request
import requests
from broker.rabbitmq import Rabbitmq
from dramatiq.common import dq_name, q_name, xq_name
import configuration.config as config

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI, APIBlueprint
from pydantic import BaseModel, Field


info = Info(title="dramatiq dashboard API documentation", version="1.0.0")
app = OpenAPI(__name__, info=info)

api = APIBlueprint("queue", __name__, url_prefix="/api")

queue_tag = Tag(name="queue", description="queue endpoints")
message_tag = Tag(name="message", description="message endpoints")

conf = config.Config()

BASE_URL = conf.base_url
RABBIT_USER = conf.rabbit_user
RABBIT_PASS = conf.rabbit_pass
VHOST = conf.vhost
DEBUG = conf.debug
HOST = conf.host
PORT = conf.port


broker = Rabbitmq(BASE_URL, RABBIT_USER, RABBIT_PASS, VHOST, HOST, PORT)


class QueuesInDetail(BaseModel):
    current_message_count: int = Field(
        0, description="current message count for this queue"
    )
    delay_message_count: int = Field(
        0, description="current delay message count for this queue"
    )
    dead_message_count: int = Field(
        0, description="current dead message count for this queue"
    )


class QueueResponse(BaseModel):
    all_messages_in_queues: int = Field(0, description="overall queue count")
    all_messages_in_delay_queues: int = Field(
        0, description="overall delay queue count"
    )
    all_messages_in_delay_queues: int = Field(
        0, description="overall delay queue count"
    )
    all_messages_in_dead_letter_queues: int = Field(
        0, description="overall dead queue count"
    )
    queue_name: QueuesInDetail


class QueueDetailResponse(BaseModel):
    current_queue_msg: dict = Field(
        [], description="dict with all of the messages in the current queue"
    )
    delay_queue_msg: dict = Field(
        [], description="dict with all of the messages in the delay queue"
    )
    dead_queue: dict = Field(
        [], description="dict with all of the messages in the dead queue"
    )


class QueuePath(BaseModel):
    queue_name: str = Field(description="queue name")


class MessagePath(BaseModel):
    queue_name: str = Field(description="queue name")
    message_id: str = Field(description="message id")


class MessageResponse(BaseModel):
    actor_name: str = Field(description="actor name")
    args: dict = Field([], description="actor name")
    kwargs: dict = Field({}, description="actor name")
    message_id: str = Field(description="actor name")
    message_timestamp: int = Field(0, description="actor name")
    options: dict = Field({}, description="options used by middelware")
    queue_name: str = Field(description="actor name")


class StatusResponse(BaseModel):
    status: str = Field(description="The status of the operation")


@api.get("/")
def api_main_page():
    return {"status": "welcome to the main page"}


@api.get(
    "/queue",
    tags=[queue_tag],
    summary="All queues",
    description="Gets the number of messages in all queues",
    responses={"200": QueueResponse},
)
def api_queues():
    return broker.get_all_queues()


@api.get(
    "/queue/<queue_name>",
    tags=[queue_tag],
    summary="Specific queue",
    description="Gets the messages in a Specific queue, like http://localhost:5000/api/queue/default",
    responses={"200": QueueDetailResponse},
)
def api_messages_of_queue(path: QueuePath):
    if path.queue_name == dq_name(path.queue_name) or path.queue_name == xq_name(
        path.queue_name
    ):
        return {"Status": "Please enter the current queue name"}
    return broker.get_messages_of_queue(path.queue_name)


@api.get(
    "/queue/<queue_name>/message/<message_id>",
    tags=[message_tag],
    summary="get message",
    description="Gets the message from a Specific queue, like http://localhost:5000/api/queue/default/message/9951e7f5-a163-4ec0-99f3-07b593239fda",
    responses={"200": MessageResponse},
)
def api_msg_details(path: MessagePath):
    return broker.get_message_details(path.queue_name, path.message_id)


@api.put(
    "/queue/<queue_name>/message/<message_id>/requeue",
    tags=[message_tag],
    summary="requeue message",
    description="moves the message from a dead or delay queue to the current queue, like http://localhost:5000/api/queue/default.DQ/message/9951e7f5-a163-4ec0-99f3-07b593239fda",
    responses={"200": StatusResponse},
)
def api_requeue_msg(path: MessagePath):
    if path.queue_name == q_name(path.queue_name):
        return {"Status": "Please enter a delay or dead queue name"}
    return broker.requeue_msg(path.queue_name, q_name(path.queue_name), path.message_id)


@api.delete(
    "/queue/<queue_name>/message/<message_id>",
    tags=[message_tag],
    summary="delete message",
    description="deletes the message from a queue, like http://localhost:5000/api/queue/default.XQ/message/9951e7f5-a163-4ec0-99f3-07b593239fda",
    responses={"200": StatusResponse},
)
def api_msg_delete(path: MessagePath):
    return broker.delete_msg(path.queue_name, path.message_id)


app.register_api(api)


@app.route("/")
def home():
    queues = requests.get(f"{request.url_root}api").json()
    return render_template("base.html", queues=queues)


@app.route("/<queue_name>")
def queue_details(queue_name):
    queues = requests.post(f"{request.url_root}api/{queue_name}").json()
    return render_template("base.html", queues=queues)


@app.route("/<queue_name>/<message_id>")
def msg_details(queue_name, message_id):
    queues = requests.post(f"{request.url_root}api/{queue_name}/{message_id}").json()
    return render_template("base.html", queues=queues)


@app.route("/requeue/<queue_name>/<message_id>")
def msg_requeue(queue_name, message_id):
    queues = requests.post(
        f"{request.url_root}api/requeue/{queue_name}/{message_id}"
    ).json()
    return render_template("base.html", queues=queues)


@app.route("/delete/<queue_name>/<message_id>")
def msg_delete(queue_name, message_id):
    queues = requests.post(
        f"{request.url_root}api/delete/{queue_name}/{message_id}"
    ).json()
    return render_template("base.html", queues=queues)


if __name__ == "__main__":
    app.run(debug=DEBUG)
