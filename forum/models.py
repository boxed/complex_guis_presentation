from django.contrib.auth.models import User
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    last_audit = models.DateTimeField(auto_now_add=True)
    auditor = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    auditor_notes = models.TextField(blank=True)

    def get_absolute_url(self):
        return '/'


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    text = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    time_created = models.DateTimeField(auto_now_add=True)


class Country(models.Model):
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    iso_code = models.CharField(max_length=2)


class Contact(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_auditor = models.BooleanField(default=False)
    phone = models.CharField(max_length=50)
    address1 = models.TextField()
    address2 = models.TextField()
    address3 = models.TextField()
    country = models.ForeignKey(Country, null=True, on_delete=models.PROTECT)
