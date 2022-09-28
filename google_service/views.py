from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from google_service.models import *
# Create your views here.


def home(request):
    """
    Главная страница
    """
    orders = Order.objects.all().order_by('id')
    dates = Order.objects.order_by('ddate').values('ddate').annotate(Sum('price_usd'))
    sum_usd = Order.objects.aggregate(Sum('price_usd')).get('price_usd__sum')
    context = {
        'orders': orders,
        'dates': dates,
        'sum': sum_usd,
    }
    return render(request, 'index.html', context=context)


def dashboard(request) -> JsonResponse:
    """
    Данные для диаграммы
    """
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
