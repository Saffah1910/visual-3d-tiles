from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .models import Order, OrderItem
# from urllib.parse import urlencode
from urllib.parse import quote_plus
import hashlib
from urllib.parse import urlencode


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    return render(request, 'store/product_detail.html', {
        'product': product
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


# def checkout(request):
#     cart = request.session.get('cart', {})

#     if not cart:
#         return redirect('product_list')

#     items = []
#     total = 0

#     for product_id, quantity in cart.items():
#         product = Product.objects.get(id=product_id)
#         subtotal = product.price * quantity
#         total += subtotal

#         items.append({
#             'product': product,
#             'quantity': quantity,
#             'subtotal': subtotal
#         })

#     if request.method == 'POST':
#         name = request.POST['name']
#         email = request.POST['email']
#         address = request.POST['address']

#         order = Order.objects.create(
#             full_name=name,
#             email=email,
#             address=address,
#             total=total
#         )

#         for item in items:
#             OrderItem.objects.create(
#                 order=order,
#                 product=item['product'],
#                 price=item['product'].price,
#                 quantity=item['quantity']
#             )

#         request.session['cart'] = {}

#         return redirect('payment', order_id=order.id)


#     return render(request, 'store/checkout.html', {
#         'items': items,
#         'total': total
#     })



def checkout(request):
    cart = request.session.get('cart', {})

    products = Product.objects.filter(id__in=cart.keys())

    total = 0
    cart_items = []

    for product in products:
        quantity = cart[str(product.id)]
        total += product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity
        })

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        order = Order.objects.create(
            customer_name=name,
            phone=phone,
            address=address,
            total_price=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        # clear cart
        request.session['cart'] = {}

        return redirect('order_success', order_id=order.id)

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })





def generate_signature(data, passphrase=""):
    encoded = urlencode(data)

    if passphrase:
        encoded += f"&passphrase={passphrase}"

    return hashlib.md5(encoded.encode()).hexdigest()



def payment(request, order_id):
    order = Order.objects.get(id=order_id)

    data = {
        "merchant_id": "10000100",
        "merchant_key": "46f0cd694581a",
        "return_url": "http://127.0.0.1:8000/",
        "cancel_url": "http://127.0.0.1:8000/cart/",
        "notify_url": "http://127.0.0.1:8000/payfast/notify/",
        "name_first": order.full_name.strip(),
        "email_address": order.email.strip(),
        "m_payment_id": str(order.id),
        "amount": f"{order.total:.2f}",
        "item_name": f"Order {order.id}",
    }

    # remove empty values
    data = {k: v for k, v in data.items() if v}

    data["signature"] = generate_signature(data)

    return render(request, "store/payment.html", {
        "payfast_url": "https://sandbox.payfast.co.za/eng/process",
        "data": data
    })

def place_order(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        cart = request.session.get('cart', {})
        total = 0

        # Create order first
        order = Order.objects.create(
            customer_name=full_name,
            email=email,
            phone=phone,
            address=address,
            total_price=0
        )

        # Save cart items
        

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            price = product.price

            total += price * quantity

            OrderItem.objects.create(
                order=order,
                product_name=product.name,
                price=price,
                quantity=quantity
            )

        # Update total
        order.total_price = total
        order.save()

        # ✅ Clear cart
        request.session['cart'] = {}

        return redirect('order_success', order_id=order.id)
    
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'store/order_success.html', {'order': order})