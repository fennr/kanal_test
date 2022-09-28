from unittest import TestCase

from django.test import TestCase
from .models import *


class OrderTestCase(TestCase):

    def test_order(self) -> Order:
        order = Order.objects.create(
            vbeln=1249708,
            ddate='2022-05-22',
            price_usd=675,
        )
        self.assertIsInstance(order, Order)
        return order

    def test_send_telegram(self):
        order = self.test_order()
        status = order.send_telegram(text='Test')
        self.assertTrue(status == 200)

class Test(TestCase):
    def test__usd_to_rub(self):
        one_usd_price = usd_to_rub()
        self.assertIsNotNone(one_usd_price)
