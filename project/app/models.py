from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=30, unique=True)
    
    def __str__(self):
        return self.name


class Mapping(models.Model):
    uid = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub = models.ManyToManyField(Subject)

    class Meta:
        ordering = ['uid']

    def __str__(self):
        return str(self.uid)

