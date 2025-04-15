from django.contrib.auth import login, authenticate, login, logout
# from . import forms
from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import SignUpForm


def logout_user(request):
    logout(request)
    return redirect('home')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('flux')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})