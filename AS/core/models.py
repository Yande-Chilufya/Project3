import os
import uuid  # For generating unique IDs
from django.db import models
from pathlib import Path  # For directory management
from django.db.models.signals import post_save
from django.dispatch import receiver


# Define the User model
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID as the primary key
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    computer_number = models.IntegerField(max_length=10)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    course = models.CharField(max_length=255)
    department = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    # Optional method to get the directory path
    def get_user_directory(self):
        return Path(f"face_encodings/{self.id}")


# Define the FaceEncoding model
class FaceEncoding(models.Model):
    user = models.ForeignKey(User, related_name='encodings', on_delete=models.CASCADE)
    encoding = models.TextField()  # Store encoding as text or string

    def __str__(self):
        return f'Face encoding for user {self.user}'


# Signal to create a directory for the user when a new user is created
@receiver(post_save, sender=User)
def create_user_directory(sender, instance, created, **kwargs):
    if created:
        user_dir = instance.get_user_directory()
        if not user_dir.exists():
            user_dir.mkdir(parents=True, exist_ok=True)
            print(f"Directory created for user {instance.id} at {user_dir}")
