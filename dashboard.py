"""import module"""
import base64
from flask import render_template, request, redirect, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from dramatiq.common import dq_name, q_name, xq_name
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI, APIBlueprint
from flask_assets import Bundle, Environment
from webassets.filter import ExternalTool
from broker.rabbitmq import Rabbitmq
from broker.module import (
    QueueResponse,
    MessagePath,
    MessageResponse,
    StatusResponse,
    QueueDetailResponse,
    QueuePath,
)
from configuration import config


conf = config.Config()

RABBITMQ_API_URL = conf.base_url
RABBITMQ_USER = conf.rabbit_user
RABBITMQ_PASS = conf.rabbit_pass
RABBITMQ_VHOST = conf.vhost
DEBUG = conf.debug
RABBITMQ_HOST = conf.host
RABBITMQ_PORT = conf.port
AUTH_USER = conf.auth_user
AUTH_PASS = conf.auth_pass

info = Info(title="dramatiq dashboard API documentation", version="1.0.0")
app = OpenAPI(__name__, info=info)
auth = HTTPBasicAuth()

if AUTH_USER and AUTH_PASS:
    BASIC_AUTH = True
    users = {AUTH_USER: generate_password_hash(AUTH_PASS)}

    AUTH_SEND = f"{AUTH_USER}:{AUTH_PASS}"
    credentials = base64.b64encode(bytes(AUTH_SEND, "utf-8")).decode()

    # create a headers object with the encoded credentials
    headers = {"Authorization": "Basic " + credentials}
else:
    BASIC_AUTH = False
    AUTH_SEND = ""
    credentials = base64.b64encode(bytes(AUTH_SEND, "utf-8")).decode()

    # create a headers object with the encoded credentials
    headers = {"Authorization": "Basic " + credentials}


# === fancy assets

app.config["ASSETS_DEBUG"] = conf.debug
assets = Environment(app)
assets.url = app.static_url_path
scss_all = Bundle("style.scss", filters="libsass", output=".webassets-cache/style.css")
assets.register("scss_all", scss_all)


class Rollup(ExternalTool):
    """bundles the typescript and the used npm libraries so that they can be used"""

    max_debug_level = None

    def input(self, infile, out, **kwargs):
        args = ["node_modules/.bin/rollup"]
        args.append("--format=iife")
        args.append(
            "-p=@rollup/plugin-node-resolve,@rollup/plugin-typescript,@rollup/plugin-commonjs"
        )
        args.append("-m=inline")
        args.append(kwargs["source_path"])
        self.subprocess(args, out, infile)


ts_all = Bundle(
    "scripts/main.ts",
    filters=(Rollup()),
    output=".webassets-cache/script.js",
    depends="**/*.ts",
)
assets.register("ts_all", ts_all)
# === fancy assets end

api = APIBlueprint("queue", __name__, url_prefix="/api")

queue_tag = Tag(name="queue", description="queue endpoints")
message_tag = Tag(name="message", description="message endpoints")


broker = Rabbitmq(
    RABBITMQ_API_URL,
    RABBITMQ_USER,
    RABBITMQ_PASS,
    RABBITMQ_VHOST,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
)


@auth.verify_password
def verify_password(username, password):
    """verifies that the password and username

    Args:
        username (str): username
        password (str): password

    Returns:
        str: the username
    """
    if BASIC_AUTH:
        if username in users and check_password_hash(users.get(username), password):  # type: ignore
            return username


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
@auth.login_required(optional=not BASIC_AUTH)
def api_queues():
    """gets the data on all the queues

    Returns:
        _type_: _description_
    """
    return jsonify(data=broker.get_all_queues())


@api.get(
    "/queue/<queue_name>",
    tags=[queue_tag],
    summary="Specific queue",
    description="Gets the messages in a Specific queue, like http://localhost:5000/api/queue/default",
    responses={"200": QueueDetailResponse},
)
@auth.login_required(optional=not BASIC_AUTH)
def api_messages_of_queue(path: QueuePath):
    """gets all the messages inside the queue

    Args:
        path (QueuePath): the QueuePath
    """
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
@auth.login_required(optional=not BASIC_AUTH)
def api_msg_details(path: MessagePath):
    """gets the details of the message inside the queue

    Args:
        path (MessagePath): MessagePath

    """
    return broker.get_message_details(path.queue_name, path.message_id)


@api.put(
    "/queue/<queue_name>/message/<message_id>/requeue",
    tags=[message_tag],
    summary="Requeue message",
    description="Moves a message from a dead or delay queue to the current queue, like http://localhost:5000/api/queue/default.DQ/message/9951e7f5-a163-4ec0-99f3-07b593239fda",
    responses={"200": StatusResponse},
)
@auth.login_required(optional=not BASIC_AUTH)
def api_requeue_msg(path: MessagePath):
    """requeue the message into the current queue

    Args:
        path (MessagePath): the MessagePath
    """
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
@auth.login_required(optional=not BASIC_AUTH)
def api_msg_delete(path: MessagePath):
    """Deletes the message of the queue

    Args:
        path (MessagePath): MessagePath
    """
    return broker.delete_msg(path.queue_name, path.message_id)


app.register_api(api)


@app.route("/")
@app.route("/queue")
@auth.login_required(optional=not BASIC_AUTH)
def all_queues():
    try:
        queues = requests.get(
            f"{request.url_root}api/queue", headers=headers, timeout=10
        ).json()
    except requests.exceptions.JSONDecodeError:
        return "<p>please enter Environment variables and basic auth credentials correctly</p>"
    del queues["data"]["chart_data"]
    return render_template("home.html", queues=queues["data"], credentials=credentials)


@app.route("/queue/<queue_name>")
@app.route("/queue/<queue_name>/current")
@auth.login_required(optional=not BASIC_AUTH)
def current_details(queue_name):
    requests.get(f"{request.url_root}api/queue", headers=headers, timeout=10)
    queues = requests.get(
        f"{request.url_root}api/queue/{queue_name}", headers=headers, timeout=10
    ).json()
    return render_template(
        "queue.html",
        queue=queues["current_queue_msg"],
        queues=queues,
        queue_name=queue_name,
        current_page="current",
        requeue=False,
        credentials=credentials,
    )


@app.route("/queue/<queue_name>/delayed")
@auth.login_required(optional=not BASIC_AUTH)
def delayed_details(queue_name):
    requests.get(f"{request.url_root}api/queue", headers=headers, timeout=10)
    queues = requests.get(
        f"{request.url_root}api/queue/{queue_name}", headers=headers, timeout=10
    ).json()
    return render_template(
        "queue.html",
        queue=queues["delay_queue_msg"],
        queues=queues,
        queue_name=queue_name,
        current_page="delay",
        requeue=True,
        credentials=credentials,
    )


@app.route("/queue/<queue_name>/failed")
@auth.login_required(optional=not BASIC_AUTH)
def failed_details(queue_name):
    requests.get(f"{request.url_root}api/queue", headers=headers, timeout=10)
    queues = requests.get(
        f"{request.url_root}api/queue/{queue_name}", headers=headers, timeout=10
    ).json()
    return render_template(
        "queue.html",
        queue=queues["dead_queue_msg"],
        queues=queues,
        queue_name=queue_name,
        dead_queue_name=xq_name(queue_name),
        current_page="dead",
        requeue=True,
        credentials=credentials,
    )


@app.route("/queue/<queue_name>/message/<message_id>")
@auth.login_required(optional=not BASIC_AUTH)
def msg_details(queue_name, message_id):
    requests.get(f"{request.url_root}api/queue", headers=headers, timeout=10)
    message = requests.get(
        f"{request.url_root}api/queue/{queue_name}/message/{message_id}",
        headers=headers,
        timeout=10,
    ).json()
    try:
        if message["status"] is not None:
            return redirect(
                f"{request.url_root}queue/{q_name(queue_name)}/current", code=302
            )
    except KeyError:
        pass

    return render_template(
        "message.html",
        message=message,
        queue_name=queue_name,
        credentials=credentials,
    )


if __name__ == "__main__":
    app.run(debug=DEBUG)
