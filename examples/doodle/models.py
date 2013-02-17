try:
    from cPickle import pickle
except ImportError:
    import pickle

from django.db import models

# Create your models here.
class DoodlePoint(models.Model):
    data_serialized = models.TextField()

    @property
    def data(self):
        return pickle.loads(str(self.data_serialized))

    @data.setter
    def data(self, value):
        self.data_serialized = pickle.dumps(value)
        return value
