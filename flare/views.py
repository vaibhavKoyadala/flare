from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from jokermanager import joker_required, no_joker, login_joker, logout_joker
import forms

@no_joker(on_fail=lambda: redirect(reverse_lazy('flare')))
def index(request):
    return render(request, template_name='flare/index.html')

@no_joker(on_fail=lambda: redirect(reverse_lazy('flare')))
def join_flare(request):
    if request.method == 'GET':
        form = forms.JoinFlareForm()

    elif request.method == 'POST':
        form = forms.JoinFlareForm(data=request.POST)
        if form.is_valid():
            joker = form.save(request.session)
            login_joker(request, joker)
            return redirect(reverse_lazy('flare'))
    return render(request,
                  template_name='flare/join_flare.html',
                  context={'form': form})

def create_flare(request):
    if request.method == 'GET':
        form = forms.CreateFlareForm()
    elif request.method == 'POST':
        form = forms.CreateFlareForm(data=request.POST)
        if form.is_valid():
            joker = form.save(request.session)
            login_joker(request, joker)
            return redirect(reverse_lazy('flare'))
    return render(  request,
                    template_name='flare/create_flare.html',
                    context={'form': form})

@joker_required(on_fail=lambda: redirect(reverse_lazy('join')))
def flare(request):
    joker = request.joker
    return render(request,
                  template_name='flare/flare.html',
                  context={'joker': joker})

@joker_required(on_fail=lambda: redirect(reverse_lazy('join')))
def logout(request):
    logout_joker(request)
    return redirect(reverse_lazy('index'))