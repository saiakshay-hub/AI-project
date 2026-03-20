from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, default="New Chat")

class Question(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE,default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    asked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question_text[:50]}"



class Internship(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    skills = models.TextField(max_length=100, blank=True,null=True)
    skills_required = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField(blank=True)
    apply_link = models.URLField()
    source = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.title} @ {self.company}"
