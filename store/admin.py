from django.contrib import admin
from .models import Product
from .models import Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'material', 'dimensions')
    search_fields = ('name', 'material')

 #register orders in admin 
admin.site.register(Order)
admin.site.register(OrderItem)