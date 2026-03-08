from django.contrib import admin
from .models import Question, Internship

# Register your models here.
admin.site.register([Question, Internship])

admin.site.site_header = "AI Guided Dashboard!"
admin.site.site_title = "AI Admin Portal"
admin.site.index_title="WElcome to Our Control Center!!"