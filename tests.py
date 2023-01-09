from broker.rabbitmq import Rabbitmq
import configuration.config as config
from dramatiq.common import dq_name, q_name, xq_name
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import requests
import random
import dramatiq
from urllib.parse import urlparse
import time
from loguru import logger
import unittest
from requests.auth import HTTPBasicAuth
import json

conf = config.Config()

BASE_URL = conf.base_url
RABBIT_USER = conf.rabbit_user
RABBIT_PASS = conf.rabbit_pass
VHOST = conf.vhost
DEBUG = conf.debug
HOST = conf.host
PORT = conf.port

rabbitmq_url = f"amqp://{RABBIT_USER}:{RABBIT_PASS}@{HOST}:{PORT}/{VHOST}"
rabbitmq_parameters = urlparse(rabbitmq_url)
broker = RabbitmqBroker(url=rabbitmq_url)
dramatiq.set_broker(broker)


class TestBroker(unittest.TestCase):
    def setUp(self):
        self.broker = Rabbitmq(BASE_URL, RABBIT_USER, RABBIT_PASS, VHOST, HOST, PORT)
        self.queue = q_name(f"t{str(random.randint(0, 1000000))}")
        self.queue_size = 5
        for i in range(self.queue_size):
            self.send_msg(self.queue, f"Hello world {i}", i)

        # This sleep is needed as rabbitmq api needs to update to reflect the change this update takes 5 secs
        time.sleep(7)

    def test_get_all_queues(self):
        """tests if the number of messages in queues is correct"""

        queues = self.broker.get_all_queues()

        self.assertEqual(queues[self.queue]["current_message_count"], self.queue_size)
        self.assertNotEqual(queues[self.queue]["delay_message_count"], self.queue_size)
        self.assertNotEqual(queues[self.queue]["dead_message_count"], self.queue_size)

    def test_get_messages_of_queue(self):
        """tests if the number of messages in a specfic queue is correct"""

        messages = self.broker.get_messages_of_queue(self.queue)

        self.assertEqual(messages["delay_queue_msg"], [])
        self.assertEqual(messages["dead_queue"], [])
        self.assertIsNotNone(messages["current_queue_msg"])

    def test_get_message_details(self):
        """tests if the message details are correct"""

        messages = self.broker.get_messages_of_queue(self.queue)

        message = json.loads(messages["current_queue_msg"][0]["payload"])

        details = self.broker.get_message_details(self.queue, message["message_id"])

        self.assertEqual(details["message_id"], message["message_id"])

    def test_requeue_msg(self):
        """tests if the ablity to requeue messages is correct"""

        messages = self.broker.get_messages_of_queue(q_name(self.queue))

        message_dq = json.loads(messages["current_queue_msg"][0]["payload"])
        message_xq = json.loads(messages["current_queue_msg"][1]["payload"])

        self.broker.requeue_msg(
            q_name(self.queue), dq_name(self.queue), message_dq["message_id"]
        )
        self.broker.requeue_msg(
            q_name(self.queue), xq_name(self.queue), message_xq["message_id"]
        )

        # This sleep is needed as rabbitmq api needs to update to reflect the change this update takes 5 secs
        time.sleep(10)

        queues = self.broker.get_all_queues()

        self.assertEqual(
            queues[q_name(self.queue)]["current_message_count"], self.queue_size - 2
        )
        self.assertEqual(queues[q_name(self.queue)]["delay_message_count"], 1)
        self.assertEqual(queues[q_name(self.queue)]["dead_message_count"], 1)

    def test_delete_msg(self):
        """tests if the ablity to delete messages is correct"""

        messages = self.broker.get_messages_of_queue(q_name(self.queue))

        message_del_1 = json.loads(messages["current_queue_msg"][0]["payload"])
        message_del_2 = json.loads(messages["current_queue_msg"][1]["payload"])

        self.broker.delete_msg(self.queue, message_del_1["message_id"])
        self.broker.delete_msg(self.queue, message_del_2["message_id"])

        # This sleep is needed as rabbitmq api needs to update to reflect the change this update takes 5 secs
        time.sleep(10)

        queues = self.broker.get_all_queues()
        self.assertEqual(
            queues[self.queue]["current_message_count"], self.queue_size - 2
        )

    def send_msg(self, queue_name, x, y):
        @dramatiq.actor(queue_name=queue_name)
        def add(x, y):
            print(x + y)

        add.send(x, y)

    def tearDown(self):
        basic = HTTPBasicAuth(RABBIT_USER, RABBIT_USER)
        requests.delete(
            url=f"{BASE_URL}/queues/{VHOST}/{q_name(self.queue)}", auth=basic
        )
        requests.delete(
            url=f"{BASE_URL}/queues/{VHOST}/{dq_name(self.queue)}", auth=basic
        )
        requests.delete(
            url=f"{BASE_URL}/queues/{VHOST}/{xq_name(self.queue)}", auth=basic
        )


if __name__ == "__main__":
    unittest.main()
