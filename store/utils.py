from .models import (Product, Order, Customer, OrderItem)
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


def getCartContext(request):
    context = {}
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        context['order'] = order
        context['items'] = items
        context['cart_items'] = order.get_cart_items
    else:
        cookie_data = getCookieData(request)
        context = cookie_data
    return context


def processGuestOrder(request, data):
    cart_data = getCartContext(request)
    name = data['form']['name']
    email = data['form']['email']
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()
    order = Order.objects.create(customer=customer, complete=False)
    items_cookie = cart_data['items']
    items_raw = list()
    for item in items_cookie:
        product = Product.objects.get(pk=item['product']['id'])
        item_obj = OrderItem(
            order=order,
            product = product,
            quantity = item['quantity']
        )
        items_raw.append(item_obj)
    OrderItem.objects.bulk_create(items_raw)
    return customer, order