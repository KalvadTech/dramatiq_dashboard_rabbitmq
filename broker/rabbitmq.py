import requests
import json
from dramatiq.common import dq_name, q_name, xq_name, current_millis
import pika
from loguru import logger
import datetime
import configuration.config as config

conf = config.Config()

chart_current_ready = []
chart_current_progress = []
chart_delay_ready = []
chart_delay_progress = []
chart_dead = []


class Rabbitmq:
    def __init__(
        self,
        rabbitmq_api_url,
        rabbitmq_user,
        rabbitmq_pass,
        rabbitmq_vhost,
        rabbitmq_host,
        rabbitmq_port,
    ):
        """Interacts with the RabbitMQ management RESTful API and pika
        to track and manage the queues and messages used by dramatiq

        Args:
            rabbitmq_api_url (str): The url of the RabbitMQ management RESTful API
            rabbit_user (str): The RabbitMQ username
            rabbit_pass (str): The RabbitMQ password
            rabbitmq_vhost (str): The vhost name
            rabbitmq_host (str): Hostname or IP Address to connect to for rabbitmq
            rabbitmq_port (int): TCP port to connect to for rabbitmq connection
        """
        self.base_url = rabbitmq_api_url
        self.auth = (rabbitmq_user, rabbitmq_pass)
        self.vhost = rabbitmq_vhost
        self.credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        self.parameters = pika.ConnectionParameters(
            rabbitmq_host, rabbitmq_port, self.vhost, self.credentials
        )

    def get_all_queues(self):
        """Get all of the queues on the specific vhost

        Returns:
            dict: A dict that has the queue names and number of messages for each queue
        """
        dict_of_queues = {}
        all_msg_current_ready = 0
        all_msg_current_progress = 0
        all_msg_delay_ready = 0
        all_msg_delay_progress = 0
        all_msg_dead = 0
        # The url used to get all queues which we send a get request to
        all_queue_url = f"{self.base_url}/queues/{self.vhost}"
        queues = requests.get(all_queue_url, auth=self.auth).json()
        # For all of the queues check if the queue has a valid queue name for dramatiq
        for queue in queues:
            if queue["name"] == q_name(queue["name"]):
                # If the name is valid then increment the all_msg_current and get the delay queue and dead queue
                all_msg_current_ready += queue["messages_ready"]
                all_msg_current_progress += queue["messages_unacknowledged"]
                queue_name = queue["name"]
                delay_queue_url = (
                    f"{self.base_url}/queues/{self.vhost}/{dq_name(queue_name)}"
                )
                dead_queue_url = (
                    f"{self.base_url}/queues/{self.vhost}/{xq_name(queue_name)}"
                )

                delay_queue = requests.get(delay_queue_url, auth=self.auth).json()
                dead_queue = requests.get(dead_queue_url, auth=self.auth).json()

                # Update dict_of_queues to have the queue name and the number of messages for the current, delay, and dead queues
                if "list_of_queues" not in dict_of_queues:
                    dict_of_queues["list_of_queues"] = {}
                dict_of_queues["list_of_queues"][queue["name"]] = {
                    "current_message_count_ready": queue["messages_ready"],
                    "current_message_count_progress": queue["messages_unacknowledged"],
                    "delay_message_count_ready": delay_queue["messages_ready"],
                    "delay_message_count_progress": delay_queue[
                        "messages_unacknowledged"
                    ],
                    "dead_message_count": dead_queue["messages"],
                }

                all_msg_delay_ready += delay_queue["messages_ready"]
                all_msg_delay_progress += delay_queue["messages_unacknowledged"]
                all_msg_dead += dead_queue["messages"]

        # Update the overall counters
        chart_current_ready.append(all_msg_current_ready)
        chart_current_progress.append(all_msg_current_progress)
        chart_delay_ready.append(all_msg_delay_ready)
        chart_delay_progress.append(all_msg_delay_progress)
        chart_dead.append(all_msg_dead)
        if chart_current_ready.__len__() >= (conf.chart_time * 60 / 5):
            chart_current_ready.pop(0)
            chart_current_progress.pop(0)
            chart_delay_ready.pop(0)
            chart_delay_progress.pop(0)
            chart_dead.pop(0)
        chart_data = {
            "chart_current_ready": chart_current_ready,
            "chart_current_progress": chart_current_progress,
            "chart_delay_ready": chart_delay_ready,
            "chart_delay_progress": chart_delay_progress,
            "chart_dead": chart_dead,
        }
        dict_of_queues.update({"chart_data": chart_data})
        dict_of_queues.update({"all_messages_in_queues_ready": all_msg_current_ready})
        dict_of_queues.update(
            {"all_messages_in_queues_progress": all_msg_current_progress}
        )
        dict_of_queues.update(
            {"all_messages_in_delay_queues_ready": all_msg_delay_ready}
        )
        dict_of_queues.update(
            {"all_messages_in_delay_queues_progress": all_msg_delay_progress}
        )
        dict_of_queues.update({"all_messages_in_dead_letter_queues": all_msg_dead})

        return dict_of_queues

    def get_messages_of_queue(self, queue_name):
        """Gets all the messages from a queue and its delay and dead queue

        Args:
            queue_name (str): The name of the queue

        Returns:
            dict: All of the messages inside the queues
        """
        # Get the messages in each queue
        current_queues = self.get_queue(queue_name)
        delay_queues = self.get_queue(dq_name(queue_name))
        dead_queues = self.get_queue(xq_name(queue_name))

        queue = {
            "current_queue_msg": self.format_queue_msg(current_queues),
            "delay_queue_msg": self.format_queue_msg(delay_queues),
            "dead_queue_msg": self.format_queue_msg(dead_queues),
        }
        return queue

    def get_message_details(self, queue_name, message_id):
        """Gets the details of a specific message

        Args:
            queue_name (str): The name of the queue
            message_id (str): The id of the message as given by dramatiq

        Returns:
            dict: the detail of the specific message
        """
        # Get the messages in queue
        messages = self.get_queue(queue_name)

        # look for the message inside the queue and return it if found
        for message in messages:
            message_json = json.loads(message["payload"])
            if message_json["message_id"] == message_id:
                message_json["created_at"] = time_since_timestamp(
                    message_json["message_timestamp"]
                )
                message_timestamp = message_json["message_timestamp"]
                message_date = datetime.datetime.fromtimestamp(
                    message_json["message_timestamp"] / 1000
                )
                message_json[
                    "message_timestamp"
                ] = f"{message_timestamp} ({message_date.astimezone()})"

                try:
                    message_json["retries"] = message_json["options"]["retries"]
                    message_json["traceback"] = message_json["options"]["traceback"]
                except KeyError:
                    message_json["retries"] = 0
                    message_json["traceback"] = ""
                del message_json["options"]
                return message_json

        return {
            "status": f"messages with ID '{message_id}' was not found in queue '{queue_name}'"
        }

    def requeue_msg(self, source_queue, destination_queue, message_id):
        """Moves one messages from one queue to another
        Args:
            source_queue (str): The queue to remove the messages from
            destination_queue (str): The queue to add the messages to
            message_id (str): The id of the message as given by dramatiq
        Returns:
            dict: Message telling us that it finished processing
        """
        # Connect to RabbitMQ server
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()

        # Declare the source and destination queues
        msg_count = channel.queue_declare(queue=source_queue, passive=True)
        channel.queue_declare(queue=destination_queue, passive=True)

        status = {
            "status": f"Error while moving message '{message_id}' from '{source_queue}' to '{destination_queue}'"
        }

        for i in range(msg_count.method.message_count):
            # Get a message from the source queue
            method_frame, header_frame, body = channel.basic_get(source_queue)
            body_json = json.loads(body)
            # If the body has the same message_id as the given id then move it to the destination_queue
            if body_json["message_id"] == message_id:
                # Change queue name to destination_queue, and eta to current UNIX time and returns it to the body
                body_json["queue_name"] = destination_queue
                body_json["options"]["eta"] = current_millis()
                body = json.dumps(body_json)
                # Add the message to the destination_queue
                channel.basic_publish(
                    exchange="", routing_key=destination_queue, body=body
                )
                # Delete the message of the source queue
                channel.basic_ack(method_frame.delivery_tag)

                status = {
                    "status": f"Moved message '{message_id}' from '{source_queue}' to '{destination_queue}'"
                }

                # To exit out of the for loop
                i = msg_count.method.message_count + 1

        # Requeue all outstanding messages
        channel.basic_nack(0, multiple=True, requeue=True)

        # Close the connection
        connection.close()
        return status

    def delete_msg(self, queue_name, message_id):
        """Delete one messages from one queue
        Args:
            queue_name (str): The queue to remove the messages from
            message_id (str): The id of the message as given by dramatiq
        Returns:
            Dict: Messages telling us that it finished processing
        """
        # Connect to RabbitMQ server
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()

        # Declare the queue
        msg_count = channel.queue_declare(queue=queue_name, passive=True)

        status = {
            "status": f"Error while Deleting message '{message_id}' from '{queue_name}'"
        }

        for i in range(msg_count.method.message_count):
            # Get a message from queue
            method_frame, header_frame, body = channel.basic_get(queue_name)
            body_json = json.loads(body)
            # If the body has the same message_id as the given id then delete the msg
            if body_json["message_id"] == message_id:
                channel.basic_ack(method_frame.delivery_tag)
                status = {
                    "Status": f"Deleted message '{message_id}' from '{queue_name}'"
                }
                i = msg_count.method.message_count + 1

        # Requeue all outstanding messages
        channel.basic_nack(0, multiple=True, requeue=True)

        # Close the connection
        connection.close()
        return status

    def format_queue_msg(self, list_of_msg):
        """a function that formats the messages that are taken from the rabbitmq api
        it stores inside a list many dicts that have the key as the actor_name+args
        and there value as the dramatiq message format

        Args:
            list_of_msg (list): list of msg inside queue

        Returns:
            current_queue_send (list): a formatted list of msg inside queue
        """
        current_queue_send = []
        for msg in list_of_msg:
            queue_json = json.loads(msg["payload"])
            actor_name = queue_json["actor_name"]
            args = queue_json["args"]
            name = f"{actor_name}{args}"
            queue_json["created_at"] = time_since_timestamp(
                queue_json["message_timestamp"]
            )
            msg_dict = {name: queue_json}
            current_queue_send.append(msg_dict)
        return current_queue_send

    def get_queue(self, queue_name):
        """Gets all the messages from a specific queue

        Args:
            queue_name (str): The name of the queue

        Returns:
            dict: All of the messages inside the queue
        """
        url = f"{self.base_url}/queues/{self.vhost}/{queue_name}/get"
        payload = json.dumps(
            {
                "count": 10000 * 10000,
                "ackmode": "ack_requeue_true",
                "encoding": "auto",
            }
        )
        response = requests.post(url, auth=self.auth, data=payload).json()
        return response


def time_since_timestamp(timestamp):
    """Calculates the amount of time that has passed from a UNIX timestamp in milliseconds

    Args:
        timestamp (int): UNIX timestamp in milliseconds

    Returns:
        str: The amount of time that has passed since the timestamp's creation
    """
    current_time = current_millis()
    time_diff = current_time - timestamp
    diff = datetime.timedelta(milliseconds=time_diff)
    total_seconds = diff.total_seconds()
    if total_seconds <= 60:
        return str(int(total_seconds)) + "s ago"
    elif total_seconds > 60 and total_seconds <= 3600:
        return str(int(total_seconds // 60)) + "m ago"
    elif total_seconds > 3600 and total_seconds <= 86400:
        return str(int(total_seconds // 3600)) + "h ago"
    elif total_seconds > 86400:
        return str(int(total_seconds // 86400)) + "d ago"
