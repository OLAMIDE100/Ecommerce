from django.urls import path
from .views import homePage,productPage,checkoutPage


urlpatterns = [
    path('',homePage,name='home'),
    path('checkout/',checkoutPage,name='checkout'),
    path('product/',productPage,name='product'),

]
