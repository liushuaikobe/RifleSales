from django.db import models
from login.models import Salesman

class Merchandise(models.Model):
    name = models.CharField(max_length = 30)
    price = models.FloatField()
    description = models.CharField(max_length = 80)
    image_path = models.URLField(max_length = 200)
    
    def __unicode__(self):
        return self.name

class Sales(models.Model):
    whosales = models.ForeignKey(Salesman)
    saleswhat = models.ForeignKey(Merchandise)
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    location = models.CharField(max_length = 50)
    count = models.IntegerField()
    
    def __unicode__(self):
        return str((self.whosales, self.saleswhat, self.count))
    