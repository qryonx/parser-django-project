import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_parser_project.settings')
django.setup()

from core.models import Product

# Удаляем все записи из таблицы Product
count = Product.objects.all().delete()
print(f"База очищена! Удалено товаров: {count[0]}")