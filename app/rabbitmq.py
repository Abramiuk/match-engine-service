import os
import json
import aio_pika

RMQ_URL = os.getenv("RMQ_URL", "amqp://guest:guest@localhost/")

async def publish_event(routing_key: str, payload: dict):
    connection = await aio_pika.connect_robust(RMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange("esports_events", aio_pika.ExchangeType.TOPIC, durable=True)
        
        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await exchange.publish(message, routing_key=routing_key)