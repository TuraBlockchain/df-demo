from django.db import models
from django.contrib.postgres.fields import JSONField
class CardInfo(models.Model):
    username = models.CharField(max_length=150)
    bio = models.TextField(null=True, blank=True)  # bio 字段允许为空
    address = models.CharField(max_length=255, primary_key=True)
    profile_image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    link = models.CharField(max_length=255)  # link 字段为字符串


class CardKV(models.Model):
    key = models.CharField(max_length=255, unique=True)
    data = JSONField()

    def __str__(self):
        return f"{self.key}: {self.data}"

