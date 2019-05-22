from django.contrib.auth.models import User
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    text = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    time_created = models.DateTimeField(auto_now_add=True)
