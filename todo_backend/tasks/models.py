import uuid
import uuid
from django.db import models

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    category = models.CharField(max_length=255, blank=True, null=True)  # Store category as a string
    telegram_user_id = models.BigIntegerField(null=True, blank=True)  # Store Telegram user ID

    def __str__(self):
        return self.title