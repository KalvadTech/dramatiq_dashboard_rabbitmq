from flask import render_template, request, redirect
import requests
from broker.rabbitmq import Rabbitmq
from dramatiq.common import dq_name, q_name, xq_name
import configuration.config as config
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI, APIBlueprint
from pydantic import BaseModel, Field
from loguru import logger


info = Info(title="dramatiq dashboard API documentation", version="1.0.0")
app = OpenAPI(__name__, info=info)

#=== fancy assets
from flask_assets import Bundle, Environment
from webassets.filter import ExternalTool

app.config['ASSETS_DEBUG'] = True
assets = Environment(app)
assets.url = app.static_url_path
scss_all = Bundle('style.scss',filters='libsass', output='.webassets-cache/style.css')
assets.register('scss_all', scss_all)
class Rollup(ExternalTool):
    max_debug_level = None
    def input(self, infile, outfile, **kwargs):
        args = ['node_modules/.bin/rollup']
        args.append("--format=iife")
        args.append("-p=@rollup/plugin-node-resolve,@rollup/plugin-typescript")
        args.append("-m=inline")
        args.append(kwargs['source_path'])
        self.subprocess(args, outfile, infile)
ts_all = Bundle(
    'script.ts',
    filters=(Rollup()),
    output='.webassets-cache/script.js',
)
assets.register('ts_all', ts_all)
#=== fancy assets end

api = APIBlueprint("queue", __name__, url_prefix="/api")

queue_tag = Tag(name="queue", description="queue endpoints")
message_tag = Tag(name="message", description="message endpoints")

conf = config.Config()

RABBITMQ_API_URL = conf.base_url
RABBITMQ_USER = conf.rabbit_user
RABBITMQ_PASS = conf.rabbit_pass
RABBITMQ_VHOST = conf.vhost
DEBUG = conf.debug
RABBITMQ_HOST = conf.host
RABBITMQ_PORT = conf.port


broker = Rabbitmq(
    RABBITMQ_API_URL,
    RABBITMQ_USER,
    RABBITMQ_PASS,
    RABBITMQ_VHOST,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
)


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


class ListOfQueues(BaseModel):
    queue_name: QueuesInDetail


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
    list_of_queues: ListOfQueues


class QueuePath(BaseModel):
    queue_name: str = Field(description="queue name")


class MessagePath(BaseModel):
    queue_name: str = Field(description="queue name")
    message_id: str = Field(description="message id")


class MessageResponse(BaseModel):
    actor_name: str = Field(description="actor name")
    args: dict = Field([], description="The vaules passed to the actor")
    kwargs: dict = Field({}, description="the keyword arguments passed to the actor")
    created_at: int = Field(0, description="how long ago the message was created")
    message_id: str = Field(description="the uuid of the message")
    message_timestamp: int = Field(
        0,
        description="the time that the message was created which is a unix timestamp in miliseconds",
    )
    retries: int = Field({}, description="number of retries for this job")
    traceback: str = Field(description="The error given from the worker")
    queue_name: str = Field(description="actor name")


class MessagesOutline(BaseModel):
    job_name: MessageResponse


class ListOfMessages(BaseModel):
    list_of_messages: MessagesOutline


class QueueDetailResponse(BaseModel):
    current_queue_msg: ListOfMessages
    delay_queue_msg: ListOfMessages
    dead_queue_msg: ListOfMessages


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
    summary="Get message",
    description="Gets the message from a Specific queue, like http://localhost:5000/api/queue/default/message/9951e7f5-a163-4ec0-99f3-07b593239fda",
    responses={"200": MessageResponse},
)
def api_msg_details(path: MessagePath):
    return broker.get_message_details(path.queue_name, path.message_id)


@api.put(
    "/queue/<queue_name>/message/<message_id>/requeue",
    tags=[message_tag],
    summary="Requeue message",
    description="Moves a message from a dead or delay queue to the current queue, like http://localhost:5000/api/queue/default.DQ/message/9951e7f5-a163-4ec0-99f3-07b593239fda",
    responses={"200": StatusResponse},
)
def api_requeue_msg(path: MessagePath):
    if path.queue_name == q_name(path.queue_name):
        return {"Status": "Please enter a delay or dead queue name"}
    return broker.requeue_msg(path.queue_name, q_name(path.queue_name), path.message_id)


@api.delete(
    "/queue/<queue_name>/message/<message_id>",
    tags=[message_tag],
    summary="Delete message",
    description="Deletes a message from a queue, like http://localhost:5000/api/queue/default.XQ/message/9951e7f5-a163-4ec0-99f3-07b593239fda",
    responses={"200": StatusResponse},
)
def api_msg_delete(path: MessagePath):
    logger.debug(path.queue_name, path.message_id)
    return broker.delete_msg(path.queue_name, path.message_id)


app.register_api(api)


@app.route("/")
@app.route("/queue")
def all_queues():
    queues = requests.get(f"{request.url_root}api/queue").json()
    return render_template("home.html", queues=queues)


@app.route("/queue/<queue_name>/current")
def current_details(queue_name):
    queues = requests.get(f"{request.url_root}api/queue/{queue_name}").json()
    return render_template(
        "queue.html",
        queue=queues["current_queue_msg"],
        queues=queues,
        queue_name=queue_name,
        current_page="current",
        requeue=False,
    )


@app.route("/queue/<queue_name>/delayed")
def delayed_details(queue_name):
    queues = requests.get(f"{request.url_root}api/queue/{queue_name}").json()
    return render_template(
        "queue.html",
        queue=queues["delay_queue_msg"],
        queues=queues,
        queue_name=queue_name,
        current_page="delay",
        requeue=True,
    )


@app.route("/queue/<queue_name>/failed")
def failed_details(queue_name):
    queues = requests.get(f"{request.url_root}api/queue/{queue_name}").json()
    return render_template(
        "queue.html",
        queue=queues["dead_queue_msg"],
        queues=queues,
        queue_name=queue_name,
        dead_queue_name=xq_name(queue_name),
        current_page="dead",
        requeue=True,
    )


@app.route("/queue/<queue_name>/message/<message_id>")
def msg_details(queue_name, message_id):
    message = requests.get(
        f"{request.url_root}api/queue/{queue_name}/message/{message_id}"
    ).json()
    try:
        if message["status"] != None:
            return redirect(
                f"{request.url_root}queue/{q_name(queue_name)}/current", code=302
            )
    except KeyError:
        pass

    return render_template("message.html", message=message, queue_name=queue_name)


if __name__ == "__main__":
    app.run(debug=DEBUG)
