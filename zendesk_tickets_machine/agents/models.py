from django.db import models


class Agent(models.Model):
    name = models.CharField(max_length=300)
    zendesk_user_id = models.CharField(max_length=100)
