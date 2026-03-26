from django.db import models

# Create your models here

class Product(models.Model):

    CATEGORY_CHOICES = [
        ('wall', 'Wall Tiles'),
        ('floor', 'Floor Tiles'),
        ('outdoor', 'Outdoor Tiles'),
    ]

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    material = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=100)
    colors = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/')

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='floor'
    )

    def __str__(self):
        return self.name

# class Order(models.Model):
#     full_name = models.CharField(max_length=200)
#     email = models.EmailField()
#     address = models.TextField()
#     total = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     paid = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Order #{self.id}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
    ]

    customer_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    address = models.TextField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()  

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     price = models.DecimalField(max_digits=8, decimal_places=2)


# class OrderItem(models.Model):
#     order = models.ForeignKey(
#         Order,
#         on_delete=models.CASCADE,
#         related_name='items'
#     )
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.product.name


