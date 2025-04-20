from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True) 
    title = models.CharField(max_length=225, verbose_name="Title")
    description = models.TextField(verbose_name="description")  
    ticket_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL , related_name="ticket_to", verbose_name="Ticket to")
    ticket_sold =  models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.ticket_id}- Ticket title{self.title} - Assigned to: {self.ticket_to}"
