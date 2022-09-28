from unittest import TestCase

from django.test import TestCase
from .models import *


class OrderTestCase(TestCase):

    def test_order(self) -> Order:
        order = Order.objects.create(
            vbeln=1249708,
            dtime='2022-05-22',
            price_usd=675,
        )
        self.assertIsInstance(order, Order)
        return order


class Test(TestCase):
    def test__usd_to_rub(self):
        one_usd_price = usd_to_rub()
        self.assertIsNotNone(one_usd_price)
