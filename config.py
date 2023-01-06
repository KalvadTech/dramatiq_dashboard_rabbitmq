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
        return os.environ.get("HOST", "localhost")

    @property
    def port(self):
        """
        Returns the port for rabbitmq
        """
        return os.environ.get("PORT", 5672)

    @property
    def base_url(self):
        """
        Returns the BASE_URL for RabbitMQ management RESTful API
        """
        return os.environ.get("BASE_URL", "")

    @property
    def rabbit_user(self):
        """
        Returns the RABBIT_USER
        """
        return os.environ.get("RABBIT_USER", "")

    @property
    def rabbit_pass(self):
        """
        Returns the RABBIT_PASS
        """
        return os.environ.get("RABBIT_PASS", "")

    @property
    def vhost(self):
        """
        Returns the VHOST
        """
        return os.environ.get("VHOST", "")

    @property
    def debug(self):
        """
        Returns the DEBUG
        """
        return os.environ.get("DEBUG", "true").lower() == "true"
