from django.db import models
from django.core.exceptions import ValidationError
import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings
from PIL import Image

class Category(models.Model):
    name= models.CharField(max_length=50, verbose_name='Название категории')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Продукт')
    item_number = models.CharField(max_length=50, unique=True, verbose_name='Артикул (SKU)')
    min_quantity = models.PositiveIntegerField(default=0, verbose_name='Минимальный остаток')
    descriptions = models.TextField(blank=True, verbose_name='Описание продукта')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Категория', related_name='products')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name='QR-код')
    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.qr_code:
            product_url = f"{settings.SITE_DOMAIN}/product/{self.pk}/"

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(product_url)
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')

            fname = f'qr_code-{self.item_number}.png'
            buffer = BytesIO()
            img.save(buffer, format='PNG')

            self.qr_code.save(fname, File(buffer), save=False)

            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Warehouse(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название склада')
    address = models.CharField(max_length=200, verbose_name='Адрес')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар', related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='Склад', related_name='stocks')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')

    def __str__(self):
        return f'{self.product.name} - {self.warehouse.name}: {self.quantity}'

    class Meta:
        verbose_name = 'Остаток на складе'
        verbose_name_plural = 'Остатки на складе'
        unique_together = ('product', 'warehouse')


class Transaction(models.Model):
    TYPES = [
        ('IN', 'Приход'),
        ('OUT', 'Расход')
    ]
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='Склад')
    transaction_type = models.CharField(max_length=10, choices=TYPES,verbose_name='Тип операции')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время')

    def __str__(self):
        return f'{self.get_transaction_type_display()} - {self.product.name} ({self.quantity}шт.)'

    def save(self, *args, **kwargs):
        stock, created = Stock.objects.get_or_create(
            product=self.product,
            warehouse=self.warehouse,
            defaults={'quantity': 0}
        )

        if self.transaction_type == 'OUT':
            if stock.quantity < self.quantity:
                raise ValidationError(
                    f"Недостаточно товара на складе! В наличии: {stock.quantity}, "
                    f"попытка списания: {self.quantity}"
                )
            stock.quantity -= self.quantity

        elif self.transaction_type == 'IN':
            stock.quantity += self.quantity

        stock.save()

        super().save(*args, **kwargs)

        # try:
        #     from telegram_bot import send_deficit_notification
        #
        #     from django.db.models import Sum
        #     total_qty = Stock.objects.filter(product=self.product).aggregate(total=Sum('quantity'))['total'] or 0
        #
        #     # Если дефицит — отправляем
        #     if total_qty < self.product.min_quantity:
        #         send_deficit_notification(
        #             product_name=self.product.name,
        #             current_qty=total_qty,
        #             min_qty=self.product.min_quantity
        #         )
        # except ImportError:
        #     pass

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'