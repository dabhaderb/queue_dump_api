import pika


class RMQ:
    def __init__(self, conn_str, default_exchange=''):
        self.conn_str = conn_str
        self.init_conn()
        self.default_exchange = default_exchange

    def init_conn(self):
        params = pika.URLParameters(self.conn_str)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

    def reinit_conn(self):
        self.connection.close()
        self.init_conn()

    def create_queue(self, queue_name, message_ack_timeout=180000):
        self.channel.queue_declare(queue=queue_name, durable=True,
                                   arguments={'x-consumer-timeout': message_ack_timeout})

    def send_one_to_queue(self, queue_name, message, exchange=None):
        properties = pika.BasicProperties(delivery_mode=2)
        exchange = exchange or self.default_exchange
        self.channel.basic_publish(exchange=exchange, body=message, routing_key=queue_name, properties=properties)

    def receive_one_from_queue(self, queue_name):
        while True:
            raw_msg = self.channel.basic_get(queue=queue_name)
            if raw_msg[0]:
                break
        return Message(self, raw_msg)

    def ack_msg(self, delivery_tag):
        self.channel.basic_ack(delivery_tag)

    def reject(self, delivery_tag):
        self.channel.basic_reject(delivery_tag, requeue=False)

    def get_queue_length(self, queue_name):
        queue_len = self.channel.queue_declare(queue_name, passive=True).method.message_count
        return queue_len


class Message:
    def __init__(self, rmq, raw_msg):
        self.rmq = rmq
        self.delivery_tag = raw_msg[0].delivery_tag
        self.msg = str(raw_msg[2])
        self.abandoned = False

    def get_msg(self):
        return self.msg

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if not self.abandoned:
            self.ack()

    def ack(self):
        self.rmq.ack_msg(self.delivery_tag)

    def abandon(self):
        self.rmq.reject(self.delivery_tag)
        self.abandoned = True