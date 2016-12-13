from django.db import models

from agents.models import Agent


class Ticket(models.Model):
    subject = models.CharField(max_length=300)
    comment = models.CharField(max_length=500)
    requester = models.CharField(max_length=100)
    requester_id = models.CharField(max_length=50)
    assignee = models.ForeignKey(Agent)
    group = models.CharField(max_length=50)
    ticket_type = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    tags = models.CharField(max_length=300)
    status = models.CharField(max_length=300)
    private_comment = models.CharField(max_length=500)
    zendesk_ticket_id = models.CharField(max_length=50)
