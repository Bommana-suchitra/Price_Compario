from django.db import models
import tensorflow as tf

class ProductImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Product Image - {self.uploaded_at}"