from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from .models import Item,OrderItem,Order
from django.views.generic import ListView,DetailView,View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin





class HomeView(ListView):

    model = Item
    paginate_by = 5
    context_object_name = 'items'
    template_name = 'home-page.html'



class OrderSummaryView(LoginRequiredMixin,View):
    def get(self,*args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user,ordered=False)

            context = {
                'order' : order
            }
            return render(self.request,'order_summary.html',context)

        except ObjectDoesNotExist:
            messages.error(self.request,"No Active Order")
            return redirect("/")




class ItemDetailView(DetailView):

    model = Item
    context_object_name = 'item'
    template_name = 'product-page.html'

def checkoutPage(request):
    
    return render(request,'checkout-page.html')

@login_required
def add_to_cart(request,slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
                                                 item=item,
                                                 user=request.user,
                                                 ordered = False)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,"this item quantity was updated")
            return  redirect('product',slug=slug)
        else:
            
            order.items.add(order_item)
            messages.info(request,"this item was added to your cart")
            return  redirect('product',slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request,"this item was added to your cart")
        return  redirect('product',slug=slug)

    

@login_required
def remove_from_cart(request,slug):

    item = get_object_or_404(Item, slug=slug)
                                       
    order_qs = Order.objects.filter(user=request.user,
                                     ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,
                                       user=request.user,
                                       ordered = False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request,"this item was removed from your cart")
            return  redirect('product',slug=slug)
        else:
            messages.info(request,"this item is not in your cart")
            return  redirect('product',slug=slug)

           
    else:
        messages.info(request,"you do not have an active order")
        return  redirect('product',slug=slug)