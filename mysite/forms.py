from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.models import User
from mysite.models import osoba, osobaWybory, wybory
from bootstrap_datepicker_plus import DateTimePickerInput




class OsobaForm(forms.Form):
    imie = forms.CharField(max_length=50, label='Imię')
    nazwisko = forms.CharField(max_length=50, label='Nazwisko')
    pesel = forms.CharField(min_length=11, max_length=11, label='Pesel')
    nr_dowodu = forms.CharField(min_length=10, max_length=10, label='Numer dowodu osobistego')


class WyboryForm(forms.Form):

    nazwaWyborow = forms.CharField(max_length=100, label='Nazwa wyborów')
    maxLiczbaKandydatowDoPoparcia = forms.IntegerField(label='Maksymalna liczba kandydatów do poparcia')
    dataRozpoczecia = forms.DateTimeField(widget=DateTimePickerInput(), label='Data rozpoczęcia')
    dataZakonczenia = forms.DateTimeField(widget=DateTimePickerInput(), label='Data zakończenia')

    def someValidation(self):
        return self.cleaned_data['dataZakonczenia'] > self.cleaned_data['dataRozpoczecia']


class OsobaWyboryForm(forms.Form):

    pesel = forms.ModelChoiceField(queryset=osoba.objects.all(), label='Osoba biorąca udział w wyborach')
    kandydat = forms.BooleanField(widget=forms.CheckboxInput(), label='Czy jest kandydatem?', required=False)


class ModForm(forms.Form):
    username = forms.CharField(max_length=50, label='Nazwa użytkownika')
    password = forms.CharField(widget=forms.PasswordInput, max_length=50, label='Hasło')
    name = forms.CharField(max_length=50, label='Imię')
    surname = forms.CharField(max_length=50, label='Nazwisko')


class LoginForm(forms.Form):
    captcha = CaptchaField()
    username = forms.CharField(max_length=50, label='Nazwa użytkownika')
    password = forms.CharField(widget=forms.PasswordInput, max_length=50, label='Hasło')