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


# ---------------------------------------------------------------------------
# Helpers for the internship listing feature
# ---------------------------------------------------------------------------

class Internship(models.Model):
    """Represents a single internship posting.

    This model is used by the internship finder page.  For simplicity the
    skills field is a comma‑separated string, but a more scalable design
    would use a separate Skill model with a many‑to‑many relationship.
    """
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    work_from_home = models.BooleanField(default=False)
    part_time = models.BooleanField(default=False)
    city = models.CharField(max_length=100, blank=True)
    stipend_min = models.IntegerField(null=True, blank=True)
    stipend_max = models.IntegerField(null=True, blank=True)
    duration_months = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    skills = models.CharField(max_length=512, blank=True,
                              help_text="Comma-separated list of skills")
    post_offer = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.company}"
