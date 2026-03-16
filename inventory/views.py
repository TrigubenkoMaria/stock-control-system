from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.contrib import messages
import tablib
from django.http import HttpResponse
from .models import Category, Product, Warehouse, Stock, Transaction
from tablib import Dataset
from .resources import ProductResource
from django.db.models import ProtectedError
from django.contrib.auth.mixins import LoginRequiredMixin

# ==========================================
# 1. ТОВАРЫ (PRODUCTS)
# ==========================================

class ProductListView(LoginRequiredMixin,ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.annotate(
            total_qty=Coalesce(Sum('stocks__quantity'), 0)
        )

class ProductDetailView(LoginRequiredMixin,DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'

class ProductCreateView(LoginRequiredMixin,CreateView):
    model = Product
    fields = ['name', 'item_number', 'category', 'min_quantity', 'descriptions']
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(LoginRequiredMixin,UpdateView):
    model = Product
    fields = ['name', 'item_number', 'category', 'min_quantity', 'descriptions']
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(LoginRequiredMixin,DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')


    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "Невозможно удалить товар! По нему есть остатки или операции в истории.")
            return redirect('product_list')


# ==========================================
# 2. КАТЕГОРИИ (CATEGORIES)
# ==========================================

class CategoryListView(LoginRequiredMixin,ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin,CreateView):
    model = Category
    fields = ['name']
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(LoginRequiredMixin,UpdateView):
    model = Category
    fields = ['name']
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(LoginRequiredMixin,DeleteView):
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')


# ==========================================
# 3. СКЛАДЫ (WAREHOUSES)
# ==========================================

class WarehouseListView(LoginRequiredMixin,ListView):
    model = Warehouse
    template_name = 'inventory/warehouse_list.html'
    context_object_name = 'warehouses'

class WarehouseCreateView(LoginRequiredMixin,CreateView):
    model = Warehouse
    fields = ['name', 'address']
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('warehouse_list')

class WarehouseUpdateView(LoginRequiredMixin,UpdateView):
    model = Warehouse
    fields = ['name', 'address']
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('warehouse_list')

class WarehouseDeleteView(LoginRequiredMixin,DeleteView):
    model = Warehouse
    template_name = 'inventory/warehouse_confirm_delete.html'
    success_url = reverse_lazy('warehouse_list')


# ==========================================
# 4. ТРАНЗАКЦИИ (ОПЕРАЦИИ ПРИХОДА/РАСХОДА)
# ==========================================

class TransactionListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name = 'inventory/transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-date']

class TransactionCreateView(LoginRequiredMixin,CreateView):
    model = Transaction
    fields = ['product', 'warehouse', 'transaction_type', 'quantity']
    template_name = 'inventory/transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)


def export_products_excel(request):
    dataset = tablib.Dataset()
    dataset.headers = ['Название', 'Артикул', 'Категория', 'Мин. остаток', 'Общий остаток']

    products = Product.objects.annotate(total_qty=Sum('stocks__quantity'))

    for p in products:
        dataset.append([
            p.name,
            p.item_number,
            p.category.name if p.category else '—',
            p.min_quantity,
            p.total_qty or 0
        ])

    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.xlsx"'

    return response





def import_products_excel(request):
    if request.method == 'POST' and request.FILES.get('import_file'):
        product_resource = ProductResource()
        dataset = Dataset()
        new_products = request.FILES['import_file']

        imported_data = dataset.load(new_products.read(), format='xlsx')

        result = product_resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            product_resource.import_data(dataset, dry_run=False)
            return redirect('product_list')
        else:
            return render(request, 'inventory/import_form.html', {'errors': result.row_errors()})

    return render(request, 'inventory/import_form.html')






