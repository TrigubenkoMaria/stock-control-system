from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Product, Category

class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name'))

    class Meta:
        model = Product
        fields = ('id', 'name', 'item_number', 'category', 'min_quantity', 'descriptions')
        import_id_fields = ('item_number',)
        skip_unchanged = True
        report_skipped = True