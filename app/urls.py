from django.urls import path
from .views import HomeView,ItemDetailView, OrderSummaryView,checkoutPage,add_to_cart,remove_from_cart,OrderSummaryView


urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('checkout/',checkoutPage,name='checkout'),
    path('product/<slug>/',ItemDetailView.as_view(),name='product'),
    path('add_to_cart/<slug>/',add_to_cart,name='add_to_cart'),
    path('remove_from_cart/<slug>/',remove_from_cart,name='remove_from_cart'),
    path('order_summary/',OrderSummaryView.as_view(),name='order_summary'),


]
