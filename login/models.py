from django.db import models

class Salesman(models.Model):
    user_name = models.CharField(max_length = 30)
    pass_word = models.CharField(max_length = 50)
    real_name = models.CharField(max_length = 30)
    
    def __unicode__(self):
        return self.user_name 
    
class Administrator(models.Model):
    user_name = models.CharField(max_length = 30)
    pass_word = models.CharField(max_length = 50)
    real_name = models.CharField(max_length = 30)
    
    def __unicode__(self):
        return self.user_name