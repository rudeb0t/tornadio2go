try:
    from cPickle import pickle
except ImportError:
    import pickle

from django.db import models

class TornadioClientManager(models.Manager):
    def broadcast(self, active_connection, event, data=None, omit_sender=False):
        server = active_connection.session.server
        for client in self.get_query_set().all():
            session = server.get_session(client.session_id)
            if session and session.session_id != active_connection.session.session_id:
                session.conn.emit(event, data)
        if not omit_sender:
            active_connection.emit(event, data)

class TornadioClient(models.Model):
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    session_info_serialized = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now_add=True, auto_now=True, editable=False)

    objects = TornadioClientManager()

    @property
    def session_info(self):
        if self.session_info_serialized:
            return pickle.loads(str(self.session_info_serialized))
        else:
            return None

    @session_info.setter
    def session_info(self, value):
        self.session_info_serialized = pickle.dumps(value)
        return value
