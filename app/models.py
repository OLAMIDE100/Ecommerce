from django.db import models
from django.urls import reverse


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
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField('this item should come with a description')


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("add_to_cart",kwargs={'slug':self.slug})

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart",kwargs={'slug':self.slug})



class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,blank=True,null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):

        return self.item.price * self.quantity

    def get_total_discount_item_price(self):

        return self.item.discount_price * self.quantity

    def get_total_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    items = models.ManyToManyField(OrderItem)

    start_date = models.DateField(auto_now_add=True)

    ordered_date = models.DateField()

    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


    
    

