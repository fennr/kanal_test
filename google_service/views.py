from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from google_service.models import *
# Create your views here.


def home(request):
    orders = Order.objects.all().order_by('id')
    dates = Order.objects.order_by('ddate').values('ddate').annotate(Sum('price_usd'))
    sum = Order.objects.aggregate(Sum('price_usd')).get('price_usd__sum')
    context = {
        'orders': orders,
        'dates': dates,
        'sum': sum,
    }
    return render(request, 'index.html', context=context)


def sum(request):
    queryset = Order.objects.all()
    sum = 0
    for order in queryset:
        sum += order.price_rub

    return JsonResponse(data={
        'sum': sum
    })

def dashboard(request):
    queryset = Order.objects.all()

    labels = []
    data = []

    for order in queryset:
        labels.append(order.ddate)
        data.append(order.price_rub)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })
