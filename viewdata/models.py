from django.db import models
from login.models import Salesman

class Commission(models.Model):
    whose = models.ForeignKey(Salesman)
    year = models.IntegerField()
    month = models.IntegerField()
    value = models.FloatField()
    havefinished = models.BooleanField()
    
    def __unicode__(self):
        return self.whose, self.month, self.havefinished