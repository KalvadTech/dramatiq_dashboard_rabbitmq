"""
Contains the config
"""


class Config:
    @property
    def localhost(self):
        """
        Returns the localhost for rabbitmq
        """
        return "localhost"

    @property
    def port(self):
        """
        Returns the port for rabbitmq
        """
        return 5672
