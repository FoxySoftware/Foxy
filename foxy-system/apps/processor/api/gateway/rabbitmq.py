from abc import abstractmethod
import json
import logging
from types import NoneType
import pika

class RabbitMQ():
    """
    Producer component that will publish message and handle
    connection and channel interactions with RabbitMQ
    """

    def __init__(self, queue_name:str, host:str, routing_key:str, username:str, password:str, exchange:str, **kwargs ):
        self._queue_name = queue_name
        self._host = host
        self._routing_key = routing_key
        self._exchange = exchange
        self._username = username
        self._password = password
        self._rabbit_passive_channel = None
        self._active_channel = None
        self._rabbit_method = None
        self._active_queue = None

    def start_server(self):
        self._connect_active()
        self._create_channel_active()
        self._create_exchange()
        self._declare_queue()
        self._create_bind()
        logging.info("Channel created...")
        
    def start_passive_server(self):
        self._connect_passive()
        self._create_channel_passive()
        self._declare_queue_passive()
    
    def _create_channel_active(self):
        self._active_channel = self._connection_active.channel()

    def close_passive_connection(self)-> None:
        self._connection_passive.close()
          
    def close_active_connection(self)-> None:
        try:
            self._connection_active.close()
        except:
            pass  
        
    def _create_channel_passive(self):
        self._rabbit_passive_channel = self._connection_passive.channel()
        return self._rabbit_passive_channel
    
    def _declare_queue_passive(self) :
        try:
            self._passive_queue = self._rabbit_passive_channel.queue_declare(queue=self._queue_name,
                                                                passive= True)
        except pika.exceptions.ChannelClosedByBroker as e:
            print(f"Queue '{self._queue_name}' does not exist: {e}")
            return None

    def _connect_active(self):
        credentials = pika.PlainCredentials(username=self._username, password=self._password)
        parameters = pika.ConnectionParameters(self._host, 
                                               credentials=credentials,
                                               connection_attempts=3,
                                                retry_delay=2,
                                                socket_timeout=10)
        self._connection_active = pika.BlockingConnection(parameters)
    
    def _connect_passive(self):
        credentials = pika.PlainCredentials(username=self._username, password=self._password)
        parameters = pika.ConnectionParameters(self._host, credentials=credentials)
        self._connection_passive = pika.BlockingConnection(parameters)

 
    def _create_exchange(self):
        self._active_channel.exchange_declare(
            exchange=self._exchange,
            exchange_type='direct',
            passive=False,
            durable=True,
            auto_delete=False
        )
    def _declare_queue(self):
        self._active_queue =  self._active_channel.queue_declare(queue=self._queue_name, durable=True)

    def _create_bind(self):
        self._active_channel.queue_bind(
            queue=self._queue_name,
            exchange=self._exchange,
            routing_key=self._routing_key
        )
        self._active_channel.basic_qos(prefetch_count=1)
    
    @abstractmethod
    def callback(self, channel, method, properties, body):
        pass

    def consume_queue(self, consumer_tag:str ):
        try:
            logging.info("Starting the server...")
            self._active_channel.basic_consume(
                queue=self._queue_name,
                on_message_callback=self.callback,
                consumer_tag=consumer_tag,
                auto_ack=False
            )

            
            self._active_channel.start_consuming()
        
        except pika.exceptions.StreamLostError as e:
            print(f"Stream connection lost: {e}")
            self._handle_connection_loss()
        
        except Exception as e:
            logging.debug(f'Exception: {e}')
            #raise Exception(f"Error consuming queue: {e}")
    
    def get_queue_message(self, limit:int = None):
        try:
            messages = []
            while True:
                method_frame, header_frame, body = self._active_channel.basic_get(queue=self._queue_name, auto_ack=False)
                
                if isinstance(limit, int):
                    if len(messages) == limit:
                        break
                
                if method_frame:
                    messages.append(body)
                    self._active_channel.basic_ack(method_frame.delivery_tag)
                else:
                    break
            self.close_active_connection()
            return messages
        except Exception as e:
            logging.debug(f'Exception: {e}')
            raise Exception(f"Error consuming queue: {e}")


    def safe_close_active_queue(self, consumer_tag:str ):
        count = self._active_queue.method.message_count
        if count != 0:
            self._active_channel.basic_cancel(consumer_tag)
        try:
            self._active_channel.stop_consuming(consumer_tag)
            self._active_channel.close()
        except Exception as e:
            logging.debug(f'Exception: {e}')
    
    def basic_cancel(self, consumer_tag:str):
        self._active_channel.basic_cancel(consumer_tag)

    def _handle_connection_loss(self):
        if self._active_channel and self._active_channel.is_open:
            self._active_channel.close()
       
    def publish(self, message={}):
        """
        :param message: message to be publish in JSON format
        """

        self._active_channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(content_type='application/json',
                                            delivery_mode=2)
        )
        logging.info("Published Message: {}".format(message))

    def count_message_in_queue(self):
        self.start_passive_server()
        message_count = self._passive_queue.method.message_count
        self.close_passive_connection()
        return message_count
     
    def is_channel_connected(self, channel)-> bool:
        if channel is None:
            return False
        try:
            # Try to perform a harmless operation to check if the channel is open
            try:
                channel.queue_declare(queue=self._queue_name, passive=True)
            except:
                return False 
            return channel.is_open
        except pika.exceptions.ChannelClosedByBroker:
            #print("Channel is closed by broker")
            return False
        except pika.exceptions.AMQPChannelError:
            #print("AMQP Channel Error")
            return False
        except pika.exceptions.AMQPConnectionError:
            #print("AMQP Connection Error")
            return False
        except Exception as e:
           # print(f"An unexpected error occurred: {e}")
            return False   
    
    def is_connection_open(self, connection)->bool:
        try:
            # Attempt a harmless operation to verify the connection
            connection.process_data_events()  # This is a no-op, just to check the connection status
            return connection.is_open
        except pika.exceptions.AMQPConnectionError:
            #print("Connection Error: The connection to RabbitMQ is not open.")
            return False
        except Exception as e:
            #print(f"An unexpected error occurred while checking connection status: {e}")
            return False

    
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

    def _queue_exists(self, queue_name):
        try:
            self._connect_passive()
            ch =self._create_channel_passive()
            ch.queue_declare(queue=queue_name, passive=True)
            self.close_passive_connection()
            return True
        except pika.exceptions.ChannelClosedByBroker:
            # Esto significa que la cola no existe
            self.close_passive_connection()
            return False