from django import forms
from models import Flare, Joker
from jokermanager import authenticate

class JoinFlareForm(forms.Form):
    flare_name = forms.CharField(max_length=30, label="What's the Flare's name?")
    password   = forms.CharField(widget=forms.PasswordInput, label="The secret password")
    joker_name = forms.CharField(max_length=30, label="What do people call you?")

    def clean_flare_name(self):
        flare_name = self.cleaned_data['flare_name']
        try:
            flare = Flare.objects.get(name__iexact=flare_name)
        except:
            raise forms.ValidationError("{flare} does not exist. \
                         Perhaps you'd like to create {flare}".format(flare=flare_name) )
        return flare_name

    def clean_password(self):
        password = self.cleaned_data['password']
        try:
            flare_name = self.cleaned_data['flare_name']
            flare = Flare.objects.get(name__iexact=flare_name)
        except: # DoesNotExist
            # The error message will already have been set in clean_flare_name, so simply return
            return password

        if authenticate(flare_name, password) is not None:
            return password

        raise forms.ValidationError("You got the password wrong !".format(flare=flare_name))

    def save(self, session):
        flare_name = self.cleaned_data['flare_name']
        joker_name = self.cleaned_data['joker_name']
        password   = self.cleaned_data['password']

        flare = authenticate(flare_name, password)

        joker = Joker(name=joker_name, flare=flare)
        joker.save()

        return joker


class CreateFlareForm(forms.Form):
    joker_name = forms.CharField(max_length=30, label="What's your name?")
    flare_name = forms.CharField(max_length=30, label="Give your gang a name")
    password   = forms.CharField(widget=forms.PasswordInput)

    def clean_flare_name(self):
        flare_name = self.cleaned_data['flare_name']
        if Flare.objects.filter(name__iexact=flare_name).exists():
            raise forms.ValidationError("{flare} already exists. \
                                        Perhaps you'd like to join {flare}.".format(flare=flare_name))
        return flare_name


    def save(self, session):
        flare_name = self.cleaned_data['flare_name']
        joker_name = self.cleaned_data['joker_name']
        password = self.cleaned_data['password']

        flare = Flare(name=flare_name, password=password)
        flare.save()

        joker = Joker(name=joker_name, flare=flare)
        joker.save()

        return joker