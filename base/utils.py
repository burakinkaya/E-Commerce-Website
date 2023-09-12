import json
from .models import *


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart:', cart)
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            print(i)
            product = Product.objects.get(product_slug=i)
            # This part may be changed, because may be not true maybe true.
            total = (product.product_price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'product_slug': product.product_slug,
                    'product_name': product.product_name,
                    'product_price': product.product_price,
                    'product_image': product.product_image,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)
            if not product.digital:
                order['shipping'] = True
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        print(items)

        for item in items:
            item.product_count_range = range(1, item.quantity + 1)
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']

    return {'cartItems': cartItems, 'order': order,'items':items}