import re
import amqp.exceptions
import kombu
import gevent
import gevent.monkey

gevent.monkey.patch_all()
# import signal
from gevent.queue import Queue

# try:
#    from gevent.lock import Semaphore
# except ImportError:
#    # older versions of gevent
#    from gevent.coros import Semaphore

class KombuClient(object):
    def __init__(self, urls, subscribe_cb):

        self._subscribe_cb = subscribe_cb

        # queue_args = {"x-ha-policy": "all"}
        self.obj_upd_exchange = kombu.Exchange('liky.test', 'fanout',
                                               durable=False)
        self._update_queue_obj = kombu.Queue("for_test", self.obj_upd_exchange,
                                             durable=False)  # ,
        # queue_arguments=queue_args)
        self._publish_queue = Queue()
        # self._conn_lock = Semaphore()

        self._conn = kombu.Connection(urls)
        self._reconnect(True)

    def _reconnect(self, delete_old_q=False):
        self._conn.close()

        self._conn.ensure_connection()
        self._conn.connect()

        self._channel = self._conn.channel()
        if delete_old_q:
            # delete the old queue in first-connect context
            # as db-resync would have caught up with history.
            try:
                bound_q = self._update_queue_obj(self._channel)
                bound_q.delete()
            except Exception as e:
                msg = 'Unable to delete the old ampq queue: %s' % (str(e))
                print msg

        self._consumer = kombu.Consumer(self._channel,
                                        queues=self._update_queue_obj,
                                        callbacks=[self._subscribe])
        self._producer = kombu.Producer(self._channel, exchange=self.obj_upd_exchange)

    def _subscribe(self, body, message):
        try:
            self._subscribe_cb(body)
        finally:
            message.ack()

    def consumer_watch(self):
        while True:
            try:
                self._consumer.consume()
                self._conn.drain_events()
            except self._conn.connection_errors + self._conn.channel_errors as e:
                print "error:" + str(e)
                self._reconnect()

    def publish(self, message):
        self._publish_queue.put(message)

    def push_msg(self):
        message = None
        while self._publish_queue.qsize() > 0:
            if not message:
                # earlier was sent fine, dequeue one more
                message = self._publish_queue.get()
            while True:
                try:
                    self._producer.publish(message)
                    message = None
                    break
                except Exception as e:
                    self._reconnect()

    def push(self, msg):
        self._producer.publish(msg)

count = 0
def show_msg(msg):
    global count
    count += 1
    print count

urls = ['pyamqp://guest:guest@172.16.119.162:5672/', 'pyamqp://guest:guest@172.16.119.163:5672/']
client = KombuClient(urls, show_msg)

# push msg
for i in xrange(10000):
    # client.push("hi")
    client.publish("hi.")
client.push_msg()
# push msg end

# consume msg
# client.consumer_watch()
# consume msg end
