from contextvars import Context
from curses import use_default_colors
from urllib import request
from django.db import models
from django.forms.forms import Form
from django.shortcuts import get_object_or_404, redirect, render
from .models import Coupon, Item,OrderItem,Order,Address,Payment,Refund
from django.views.generic import ListView,DetailView,View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm,CouponForm,RequestRefundForm
from django.conf import settings
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY 

import string
import random

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits + string.ascii_uppercase,k=20))



def is_valid_form(values):
    valid = True
    for fields in values:
        if fields == '':
            valid = False
    return valid





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


class PaymentView(View):
    def get(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)
        if order.billing_address:
            context = {
                'order' : order,
                'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request,"payment.html",context)

        else:
            messages.warning(self.request, "You dont have a billing addres")
            return redirect("checkout")


    def post(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)
        token =  self.request.POST.get('stripeToken')
        amount= int(order.get_total() * 100)



        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(amount=amount,
                              currency="usd",
                                source=token,
                                description="My First Test Charge (created for API docs)",)

            
            
            
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()


            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()




            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            messages.success(self.request,"Your Order was successful")
            return redirect('/')
        
        
        except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
           body = e.json_body
           err = body.get('error',{})
           messages.error(self.request,f"{err.get('message')}")
           return redirect("/")
        except stripe.error.RateLimitError as e:

            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")


class CheckoutView(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            form = CheckoutForm()
            context = {
                'order' : order,
                'form' : form,
                'couponform' : CouponForm(),
                'DISPLAY_COUPON_FORM': True,
            }

            shipping_address_qs = Address.objects.filter(user=self.request.user,
                                                         address_type="S",
                                                         default=True)

            if shipping_address_qs.exists():
                context.update({"default_shipping_address" : shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(user=self.request.user,
                                                         address_type="B",
                                                         default=True)

            if billing_address_qs.exists():
                context.update({"default_billing_address" : billing_address_qs[0]})



            return render(self.request,'checkout-page.html',context)
        except ObjectDoesNotExist:
            messages.error(self.request,"No Active Order")
            return redirect("checkout")


    def post(self,*args,**kwargs):

        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user,ordered=False)

            if form.is_valid():

                use_default_shipping = form.cleaned_data.get("use_default_shipping")
                if use_default_shipping:
                    address_qs = Address.objects.filter(user=self.request.user,
                                                         address_type="S",
                                                         default=True)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request,"No available default shipping address")
                        return redirect('checkout')
                else:
                    shipping_address1 = form.cleaned_data.get('shipping_address1')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    
                    if is_valid_form([shipping_address1,shipping_country,shipping_zip]):
                        shipping_address = Address(user = self.request.user,
                                                    street_address = shipping_address1,
                                                    apartment_address = shipping_address2,
                                                    country = shipping_country,
                                                    zip = shipping_zip,
                                                    address_type = "S"
                                                    )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get("set_default_shipping")
                        if set_default_shipping:
                            shipping_address.default =True
                            shipping_address.save()
                        
                    else:
                        messages.info(self.request," kindly fill the required field")

                use_default_billing = form.cleaned_data.get("use_default_billing")

                same_billing_address = form.cleaned_data.get("same_billing_address")

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()


                elif use_default_billing:
                    address_qs = Address.objects.filter(user=self.request.user,
                                                         address_type="B",
                                                         default=True)
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()

                    else:
                        messages.info(self.request,"No available default billing address")
                        return redirect('checkout')
                else:
                    billing_address1 = form.cleaned_data.get('billing_address1')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    
                    if is_valid_form([billing_address1,billing_country,billing_zip]):
                        billing_address = Address(user = self.request.user,
                                                    street_address = billing_address1,
                                                    apartment_address = billing_address2,
                                                    country = billing_country,
                                                    zip = billing_zip,
                                                    address_type = "B"
                                                    )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get("set_default_billing")
                        if set_default_billing:
                            billing_address.default =True
                            billing_address.save()
                        
                    else:
                        messages.info(self.request," kindly fill the required field")
                        return redirect('checkout')


                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'P':
                    return redirect('payment',payment_option = 'paystack')

                elif payment_option == 'F':
                    return redirect('payment',payment_option = 'flutterwave')

                else:
                     messages.error(self.request,"invalid payment optiion selected")
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

def get_coupon(request,code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon

    except ObjectDoesNotExist:
        messages.info(request,'Coupon code does not exist')
        return redirect('checkout')

class AddCoupon(View):
    def post(self,*args,**kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user,ordered=False)
                order.coupon = get_coupon(self.request,code)
                order.save()
                messages.info(self.request,'Sucessfuly added coupon')
                return redirect('checkout')
           
            except ObjectDoesNotExist:
                messages.info(self.request,'You do not have an Active Order')
                return redirect('checkout')

class RequestRefundView(View):
    def get(self,*args,**kwargs):
        form = RequestRefundForm()
        context = {
            'form': form
        }
        return render(self.request,'request_refund.html',context)
    def post(self,*args,**kwargs):
        form = RequestRefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email  = form.cleaned_data.get('email')
            try:
                order=Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

               
                refund = Refund(reason=message,order=order,email=email)
                refund.save()
                messages.info(self.request,'refund request successfully lodge')
                return redirect("/")

            except ObjectDoesNotExist:
                 messages.info(self.request,'such order does not exist')
                 return redirect("request_refund")


