from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    price = models.CharField(max_length=100, verbose_name="Цена")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title