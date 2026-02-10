from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .models import Order, OrderItem
from urllib.parse import urlencode
import hashlib




def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products
    })


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    cart[str(product_id)] = cart.get(str(product_id), 0) + 1

    request.session['cart'] = cart

    return redirect('view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total
    })

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart

    return redirect('view_cart')


def update_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            cart[str(product_id)] = quantity
        else:
            del cart[str(product_id)]

    request.session['cart'] = cart

    return redirect('view_cart')


def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('product_list')

    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        address = request.POST['address']

        order = Order.objects.create(
            full_name=name,
            email=email,
            address=address,
            total=total
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['product'].price,
                quantity=item['quantity']
            )

        request.session['cart'] = {}

        return redirect('payment', order_id=order.id)


    return render(request, 'store/checkout.html', {
        'items': items,
        'total': total
    })

def generate_signature(data, passphrase=""):
    output = ""

    for key in sorted(data.keys()):
        value = data[key]
        if value != "":
            output += f"{key}={value}&"

    output = output[:-1]  # remove last &

    if passphrase:
        output += f"&passphrase={passphrase}"

    return hashlib.md5(output.encode()).hexdigest()


def payment(request, order_id):
    order = Order.objects.get(id=order_id)

    # PAYFAST SANDBOX DETAILS
    merchant_id = "10000100"
    merchant_key = "46f0cd694581a"
    passphrase = ""  # sandbox = empty

    return_url = request.build_absolute_uri('/')
    cancel_url = request.build_absolute_uri('/cart/')
    notify_url = request.build_absolute_uri('/payfast/notify/')

    data = {
        # Merchant
        "merchant_id": merchant_id,
        "merchant_key": merchant_key,

        # URLs
        "return_url": return_url,
        "cancel_url": cancel_url,
        "notify_url": notify_url,

        # Buyer
        "name_first": order.full_name,
        "email_address": order.email if order.email else "test@example.com",


        # Transaction
        "m_payment_id": str(order.id),
        "amount": "%.2f" % order.total,
        "item_name": f"Order {order.id}",
    }

    # Generate correct signature
    signature = generate_signature(data, passphrase)
    data["signature"] = signature

    return render(request, "store/payment.html", {
        "data": data
    })