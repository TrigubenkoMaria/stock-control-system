from django.urls import path
from . import views

urlpatterns = [
    # Товары
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Категории
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Склады
    path('warehouses/', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouse/add/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouse/<int:pk>/edit/', views.WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('warehouse/<int:pk>/delete/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),

    # Транзакции (Приход/Расход)
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transaction/add/', views.TransactionCreateView.as_view(), name='transaction_create'),

    path('export/excel/', views.export_products_excel, name='export_excel'),
    path('import/excel/', views.import_products_excel, name='product_import'),
]