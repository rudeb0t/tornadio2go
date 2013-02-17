# Ported from tornadio2-draw sample app by Hyliker Cheung.
# See: https://github.com/hyliker/tornadio2-draw
#
import collections
import datetime
import time
import simplejson as json
import tornadio2

from models import DoodlePoint
from tornadio2go.models import TornadioClient

try:
    from cPickle import pickle
except ImportError:
    import pickle

def get_unixtimestamp():
    x = datetime.datetime.now()
    return (time.mktime(x.timetuple()) * 1e3 + x.microsecond / 1e3)

class SocketIOConnection(tornadio2.SocketConnection):
    users = set()
    drawDataList = collections.deque(maxlen=1000)

    def on_open(self, info):
        client = TornadioClient()
        client.session_id = self.session.session_id
        client.session_info = self.session.info
        client.save()

        TornadioClient.objects.broadcast(self, 'online', TornadioClient.objects.count())

    @tornadio2.event
    def update(self):
        for doodle in DoodlePoint.objects.all():
            json_data = json.loads(doodle.data)
            json_data['timestamp'] = get_unixtimestamp()
            self.emit("draw", json.dumps(json_data))

    def on_message(self, message):
        TornadioClient.objects.broadcast(self, 'message', message, omit_sender=True);

    @tornadio2.event
    def calibrate(self, message):
        json_data = json.loads(message)
        ts = get_unixtimestamp()
        td = json_data['timestamp'] - ts
        ret = dict(timestamp=ts, timediff=td)
        self.emit('calibrate', json.dumps(ret))

    @tornadio2.event
    def clear(self):
        DoodlePoint.objects.all().delete()
        TornadioClient.objects.broadcast(self, 'clear')

    @tornadio2.event
    def draw(self, message):
        json_message = json.loads(message)
        json_message['timestamp'] = get_unixtimestamp()
        doodle = DoodlePoint()
        doodle.data = message
        doodle.save()
        TornadioClient.objects.broadcast(self, 'draw', json.dumps(json_message))

    def on_close(self):
        try:
            client = TornadioClient.objects.get(session_id=self.session.session_id)
        except TornadioClient.DoesNotExist:
            pass
        else:
            client.delete()

        TornadioClient.objects.broadcast(self, 'online', TornadioClient.objects.count(), omit_sender=True)
