"""
Contains the config
"""
import os


class Config:
    @property
    def host(self):
        """
        Returns the host for rabbitmq
        """
        return os.environ.get("RABBITMQ_HOST", "localhost")

    @property
    def port(self):
        """
        Returns the port for rabbitmq
        """
        return os.environ.get("RABBITMQ_PORT", 5672)

    @property
    def base_url(self):
        """
        Returns the BASE_URL for RabbitMQ management RESTful API
        """
        return os.environ.get("RABBITMQ_API_URL", "")

    @property
    def rabbit_user(self):
        """
        Returns the RABBITMQ_USER
        """
        return os.environ.get("RABBITMQ_USER", "")

    @property
    def rabbit_pass(self):
        """
        Returns the RABBITMQ_PASS
        """
        return os.environ.get("RABBITMQ_PASS", "")

    @property
    def vhost(self):
        """
        Returns the VHOST
        """
        return os.environ.get("RABBITMQ_VHOST", "")

    @property
    def debug(self):
        """
        Returns the DEBUG
        """
        return os.environ.get("DEBUG", "false").lower() == "true"
