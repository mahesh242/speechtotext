from django.db import models

# Create your models here.

class Audio(models.Model):
    audio_file = models.FileField(upload_to='audio_files/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.audio_file

class TestText(models.Model):
    text = models.TextField(verbose_name="Text")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
