from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'image_preview',
        'name',
        'price',
        'category',
        'material',
        'dimensions'
    )

    list_editable = ('price',)

    search_fields = ('name', 'material')
    list_filter = ('category',)

    ordering = ('price',)

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />',
            obj.image.url
        )

    image_preview.short_description = "Image"


admin.site.register(Order)
admin.site.register(OrderItem)