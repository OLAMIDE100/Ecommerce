from django.db import models
from django.forms.forms import Form
from django.shortcuts import get_object_or_404, redirect, render
from .models import Item,OrderItem,Order,BillingAddress
from django.views.generic import ListView,DetailView,View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm






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




class CheckoutView(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)

        form = CheckoutForm()

        context = {
            'order' : order,
            'form' : form
        }
        return render(self.request,'checkout-page.html',context)

    def post(self,*args,**kwargs):

        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user,ordered=False)

            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                #same_billing_address = form.cleaned_data.get('same_billing_address')
                #save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                billing_address = BillingAddress(user = self.request.user,
                                                street_address = street_address,
                                                apartment_address = apartment_address,
                                                country = country,
                                                zip = zip,
                                                #same_billing_address = same_billing_address,
                                                #save_info = save_info,
                                                #payment_option = payment_option
                                                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                return redirect('checkout')
            messages.error(self.request,"failed checkout")
            return redirect('checkout')

        except ObjectDoesNotExist:
            messages.error(self.request,"No Active Order")
            return redirect("/")
   




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
            return  redirect('order_summary')
        else:
            
            order.items.add(order_item)
            messages.info(request,"this item was added to your cart")
            return  redirect('order_summary')
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
            return  redirect('order_summary')
        else:
            messages.info(request,"this item is not in your cart")
            return  redirect('product',slug=slug)

           
    else:
        messages.info(request,"you do not have an active order")
        return  redirect('product',slug=slug)

def remove_item_from_cart(request,slug):

    item = get_object_or_404(Item, slug=slug)
                                       
    order_qs = Order.objects.filter(user=request.user,
                                     ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,
                                       user=request.user,
                                       ordered = False)[0]
            if order_item.quantity == 1:
                order.items.remove(order_item)
                order_item.delete()
                messages.info(request,"item was removed from your cart")
                return  redirect('order_summary')
            else:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request,"single item was removed from your cart")
                return  redirect('order_summary')
        else:
            messages.info(request,"this item is not in your cart")
            return  redirect('product',slug=slug)

           
    else:
        messages.info(request,"you do not have an active order")
        return  redirect('product',slug=slug)


@login_required
def add_item_to_cart(request,slug):
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
            return  redirect('order_summary')
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