import json
import logging

import pika


class RabbitMQ():

    def __init__(self, queue, host, routing_key, username, password, exchange=''):
        self._queue = queue
        self._host = host
        self._routing_key = routing_key
        self._exchange = exchange
        self._username = username
        self._password = password
        self.start_server()

    def start_server(self):
        self.create_channel()
        self.create_exchange()
        self.create_bind()
        logging.info("Channel created...")

    def create_channel(self):
        credentials = pika.PlainCredentials(username=self._username, password=self._password)
        parameters = pika.ConnectionParameters(self._host, credentials=credentials)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

    def create_exchange(self):
        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type='direct',
            passive=False,
            durable=True,
            auto_delete=False
        )
        self._channel.queue_declare(queue=self._queue, durable=True)

    def create_bind(self):
        self._channel.queue_bind(
            queue=self._queue,
            exchange=self._exchange,
            routing_key=self._routing_key
        )

    def publish(self, message={}):
        """
        :param message: message to be publish in JSON format
        """

        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(content_type='application/json',
                                            delivery_mode=2)
        )
        logging.info("Published Message: {}".format(message))


    def delete_queue_and_unbind_from_exchange(self):
        pass
        # Delete a queue
        # queue_name = 'my_queue'
        # channel.queue_delete(queue=queue_name)
        # print(f"Queue '{queue_name}' deleted.")

        # # Unbind a routing key from an exchange
        # exchange_name = 'my_exchange'
        # routing_key = 'my_routing_key'
        # channel.queue_unbind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)
        # print(f"Routing key '{routing_key}' unbound from exchange '{exchange_name}'.")

