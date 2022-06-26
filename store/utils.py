from .models import (Product,)
import json

def getCookieData(request):
    context = dict()
    order = {"get_cart_items":0, "get_cart_total":0, "shipping_able":False}
    try:
        cart_cookie = json.loads(request.COOKIES['cart'])
    except KeyError:
        cart_cookie = {}
    items = []
    order['get_cart_items'] = sum([cart_cookie[i]['quantity'] for i in cart_cookie])
    for i in cart_cookie:
        try:
            product = Product.objects.get(pk=i)
        except Product.DoesNotExist:
            continue
        quantity = cart_cookie[i]['quantity']
        if (product.digital == False) and (order['shipping_able'] == False):
            order['shipping_able'] = True
        total = product.price * quantity
        order['get_cart_total'] += total
        item = {
            'product': {
                'id':product.id,
                'name':product.name,
                'image':product.image,
                'price':product.price
            },
            'quantity':quantity,
            'get_total':total
        }
        items.append(item)
    context['order'] = order
    context['items'] = items
    context['cart_items'] = order['get_cart_items']
    return context