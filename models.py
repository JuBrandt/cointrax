from django.db import models
from django import forms

from captcha.fields import CaptchaField


class PaymentAddress(models.Model):
    btc_address = models.CharField(max_length=35)
    available = models.BooleanField(default=True)


class Registration(models.Model):
    full_name = models.CharField(max_length=100)
    email_address = models.CharField(max_length=254)
    btc_price = models.DecimalField(max_digits=8, decimal_places=2)
    payment_usd = models.DecimalField(max_digits=5, decimal_places=2)
    payment_btc = models.IntegerField()
    btc_address = models.CharField(max_length=35)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class RegistrationForm(forms.Form):
    full_name = forms.CharField(
        label='Name', max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Full name'})
    )
    email_address = forms.EmailField(label='Email address', max_length=254)
    captcha = CaptchaField(label='')
    btc_price = forms.DecimalField(max_digits=8, decimal_places=2,
                                   widget=forms.HiddenInput())
    payment_usd = forms.DecimalField(
        label='Payment (USD)', min_value=0, max_digits=5, decimal_places=2,
        widget=forms.TextInput(attrs={'placeholder': 'Dollars'})
    )
