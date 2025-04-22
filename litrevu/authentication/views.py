from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm


def logout_user(request):
    logout(request)
    return redirect('home')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') # Rediriger vers la page d'accueil après l'inscription
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


@login_required
def profile(request):
    # Vue de profil simple pour l'instant
    return render(request, 'authentication/profile.html')