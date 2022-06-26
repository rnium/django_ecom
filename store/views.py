from django.shortcuts import render
from .models import (Order, Product, OrderItem, ShippingAddress)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime


def store(request):
    context = {}
    context['products'] = Product.objects.all()
    if request.user.is_authenticated:
        customer = request.user.customer
        try:
            order = Order.objects.get(customer=customer, complete=False)
            context['cart_items'] = order.get_cart_items
        except Order.DoesNotExist:
            context['cart_items'] = 0
    else:
        try:
            cart_cookie = json.loads(request.COOKIES['cart'])
        except KeyError:
            cart_cookie = {}
        cart_items = sum([cart_cookie[i]['quantity'] for i in cart_cookie])
        context['cart_items'] = cart_items

    return render(request, 'store/store.html', context=context)


def cart(request):
    context = {}
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        context['order'] = order
        context['items'] = items
    else:
        order = {"get_cart_items":0, "get_cart_total":0}
        try:
            cart_cookie = json.loads(request.COOKIES['cart'])
        except KeyError:
            cart_cookie = {}
        items = []
        order['get_cart_items'] = sum([cart_cookie[i]['quantity'] for i in cart_cookie])
        for i in cart_cookie:
            product = Product.objects.get(pk=i)
            quantity = cart_cookie[i]['quantity']
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
    return render(request, 'store/cart.html', context=context)


def checkout(request):
    context = {}
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        context['order'] = order
        context['items'] = items
    else:
        order = {"get_cart_items":0, "get_cart_total":0, "shipping_able":False}
        try:
            cart_cookie = json.loads(request.COOKIES['cart'])
        except KeyError:
            cart_cookie = {}
        items = []
        order['get_cart_items'] = sum([cart_cookie[i]['quantity'] for i in cart_cookie])
        for i in cart_cookie:
            product = Product.objects.get(pk=i)
            quantity = cart_cookie[i]['quantity']
            if (product.digital == False) and (order['shipping_able'] == False):
                order['shipping_able'] = True
            total = product.price * quantity
            order['get_cart_total'] += total
            item = {
                'product': {
                    'name':product.name,
                    'image':product.image,
                    'price':product.price
                },
                'quantity':quantity
            }
            items.append(item)
        context['order'] = order
        context['items'] = items
        context['cart_items'] = order['get_cart_items']
    return render(request, 'store/checkout.html', context=context)


def updateOrderItem(request):
    if request.method == "GET":
        response = JsonResponse({"error": "method not allowed"})
        response.status_code = 405
        return response
    else:
        data = json.loads(request.body)
        print(data)
        product_id = data.get('productID')
        action = data.get('action')
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        product = Product.objects.get(pk=product_id)
        orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)
        if action == 'add':
            orderitem.quantity = orderitem.quantity + 1
        elif action == 'remove':
            orderitem.quantity = orderitem.quantity - 1
        orderitem.save()
        if orderitem.quantity <= 0:
            orderitem.delete()
        return JsonResponse({"ok":True})


def processOrder(request):
    data = json.loads(request.body)
    trx_id = datetime.datetime.now().timestamp()
    trx_id = str(trx_id).replace('.','')
    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.get(customer=customer, complete=False)
        if order.shipping_able:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
            )
        if order.get_cart_total == float(data['form']['total']):
            order.transaction_id = trx_id
            order.complete = True
            order.save()
    else:
        response = JsonResponse("user not logged in", safe=False)
        response.status_code = 403
        return response
            
    return JsonResponse("order processed!", safe=False)