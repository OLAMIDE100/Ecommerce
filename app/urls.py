from django.urls import path
from .views import (HomeView,ItemDetailView, OrderSummaryView,CheckoutView,
                    add_to_cart,remove_from_cart,OrderSummaryView,
                    remove_item_from_cart,add_item_to_cart,PaymentView)


urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('checkout/',CheckoutView.as_view(),name='checkout'),
    path('product/<slug>/',ItemDetailView.as_view(),name='product'),
    path('add_to_cart/<slug>/',add_to_cart,name='add_to_cart'),
    path('remove_from_cart/<slug>/',remove_from_cart,name='remove_from_cart'),
    path('order_summary/',OrderSummaryView.as_view(),name='order_summary'),
    path('remove_item_from_cart/<slug>/',remove_item_from_cart,name='remove_item_from_cart'),
    path('add_item_to_cart/<slug>/',add_item_to_cart,name='add_item_to_cart'),
    path('payment/<payment_option>/',PaymentView.as_view(),name='payment')

]
