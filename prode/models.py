from __future__ import unicode_literals

from django.db import models

class Goods(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    fare = models.DecimalField(max_digits=7, decimal_places=2)
    tax = models.DecimalField(max_digits=7, decimal_places=2)
    currency = models.CharField(max_length=50)
    brand = models.CharField(max_length=100)
    description = models.CharField(max_length=1024)
