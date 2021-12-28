from django.db import models

from django.conf import settings


CATEGORY_CHOICES = (
    ('S','Shirt'),
    ('SW','Sport Wear'),
    ('O','Out Weat')
)

LABEL_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)



class Item(models.Model):
    drink_name = models.CharField(max_length=100)
    drink_price = models.IntegerField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)


    def __str__(self):
        return self.drink_name



class OrderItem(models.Model):
    drink = models.ForeignKey(Item,on_delete=models.CASCADE)

    def __str__(self):
        return self.drink_name



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    drinks = models.ManyToManyField(OrderItem)

    start_date = models.DateField(auto_now_add=True)

    ordered_date = models.DateField()

    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.drink_name

