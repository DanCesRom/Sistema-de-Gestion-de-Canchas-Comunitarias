from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string
from django.utils.timezone import now
from utils.encryption import encrypt_data, decrypt_data 



class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculine'),
        ('F', 'Feminine'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    biometric_enabled = models.BooleanField(default=False)

    _id_document = models.TextField(db_column='id_document')

    @property
    def id_document(self):
        try:
            return decrypt_data(self._id_document)
        except Exception:
            return None

    @id_document.setter
    def id_document(self, value):
        self._id_document = encrypt_data(value)

    def __str__(self):
        return self.user.email

class Place(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    open_days = models.CharField(max_length=50)
    description = models.TextField()
    image_url = models.CharField(blank=True, max_length=255)
    sport_type = models.TextField(blank=True, null=False, default='')

    def __str__(self):
        return self.name

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    qr_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.user.username} - {self.place.name} - {self.date} ({self.start_time}-{self.end_time})"


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

class SupportContact(models.Model):
    support_email = models.EmailField()
    support_phone = models.CharField(max_length=20)
