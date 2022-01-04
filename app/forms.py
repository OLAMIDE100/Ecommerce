from django import forms
from django.forms.widgets import TextInput
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget




PAYMENT_CHOICES = (
    ('P','PAYSTACK'),
    ('F','FLUTTERWAVE')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget= forms.TextInput(attrs={
        'placeholder' : "1234 Main St"
    }))

    apartment_address = forms.CharField(widget= forms.TextInput(attrs={
        'placeholder' : "Apartment or suite"
    }),required=False)

    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs = {
        'class' :"custom-select d-block w-100" 
    }))

    zip = forms.CharField(widget=TextInput(attrs = {
        'class' : "form-control"
    }))
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(choices= PAYMENT_CHOICES,widget=forms.RadioSelect())