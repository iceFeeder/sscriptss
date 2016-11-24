import kazoo.client
import kazoo.exceptions
import kazoo.handlers.gevent
import kazoo.recipe.election
from kazoo.client import KazooState
from kazoo.retry import KazooRetry
import gevent
import os
import uuid

class zkClient(object):
    def __init__(self,server_list):
        self._retry = KazooRetry(max_tries=None, max_delay=300,
                                 sleep_func=gevent.sleep)
        self._zk_client = kazoo.client.KazooClient(
                server_list,
                timeout=400,
                handler=kazoo.handlers.gevent.SequentialGeventHandler(),
                connection_retry=self._retry,
                command_retry=self._retry)

        self._zk_client.add_listener(self._zk_listener)
        self._election = None
        self._server_list = server_list

        self._conn_state = None
        self._lost_cb = None

        self.connect()

    def _zk_listener(self, state):
        if state == KazooState.CONNECTED:
            if self._election:
                self._election.cancel()
        elif state == KazooState.LOST:
            if self._lost_cb:
                self._lost_cb()
            else:
                os._exit(2)
        elif state == KazooState.SUSPENDED:
            pass

    def connect(self):
        while True:
            try:
                self._zk_client.start()
                break
            except gevent.event.Timeout as e:
                gevent.sleep(1)
            except Exception as e:
                gevent.sleep(1)

    def is_connected(self):
        return self._zk_client.state == KazooState.CONNECTED

    def master_election(self, path, identifier, func, *args, **kwargs):
        self._election = self._zk_client.Election(path, identifier)
        self._election.run(func, *args, **kwargs)

    def create_node(self, path, value=None):
        try:
            if value is None:
                value = uuid.uuid4()
            retry = self._retry.copy()
            retry(self._zk_client.create, path, str(value), makepath=True)
        except kazoo.exceptions.NodeExistsError:
            current_value = self.read_node(path)
            if current_value == value:
                return True;
            raise Exception("create node path %s, value %s" % (path,value))
    # end create_node

    def delete_node(self, path, recursive=False):
        try:
            retry = self._retry.copy()
            retry(self._zk_client.delete, path, recursive=recursive)
        except kazoo.exceptions.NoNodeError:
            pass
        except Exception as e:
            raise e
    # end delete_node

    def read_node(self, path, include_timestamp=False):
        try:
            retry = self._retry.copy()
            value = retry(self._zk_client.get, path)
            if include_timestamp:
                return value
            return value[0]
        except Exception:
            return None
    # end read_node

def run():
    for i in range(10):
        print i
        gevent.sleep(3)
    print "done"

def test_election(client):
    for i in range(3):
        client.master_election("/for_test",os.getpid(),run)

client = zkClient("127.0.0.1:2181")
