from django.contrib import admin
from speechtotext.models import Audio, TestText
# Register your models here.

admin.site.register(Audio)
admin.site.register(TestText)