from django.shortcuts import render
from .models import Item

def homePage(request):

    return render(request,'home-page.html')


def checkoutPage(request):

    return render(request,'checkout-page.html')


def productPage(request):


    return render(request,'product-page.html')