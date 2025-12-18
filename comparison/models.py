from django.db import models
import tensorflow as tf

class ProductImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    #predicted_name = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.predicted_name or f"Image {self.id}"