from aiohttp import web
from api.gateway.rabbitmq import RabbitMQ


class Handler():

    def __init__(self, rabbitmq:RabbitMQ) -> None:
        self.rabbitmq = rabbitmq

    def publish_data(self, data):
        self.rabbitmq.publish(message={"data": data})
        return web.json_response({'message': "ok"})

    async def publish(self, request):
        body = await request.json()
        self.rabbitmq.publish(message={"data": body})
        return web.json_response({'message': body})
