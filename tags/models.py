from django.db import models

class CardInfo(models.Model):
    username = models.CharField(max_length=150)
    bio = models.TextField(null=True, blank=True)  # bio 字段允许为空
    address = models.CharField(max_length=255, primary_key=True)
    profile_image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    link = models.CharField(max_length=255)  # link 字段为字符串