from django.contrib import admin
from .models import Category, Product, Warehouse, Stock, Transaction
from import_export.admin import ImportExportModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('name', 'category', 'item_number', 'min_quantity')

    search_fields = ('name', 'item_number')

    list_filter = ('category',)

    inlines = [StockInline]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity')
    list_filter = ('warehouse', 'product__category')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'transaction_type', 'quantity', 'date')
    list_filter = ('transaction_type', 'warehouse', 'date')
    search_fields = ('product__name',)