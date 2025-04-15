"""
URL configuration for litrevu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import authentication.views
import app.views

from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(
        template_name='authentication/login.html',
        redirect_authenticated_user=True),
        name='login'),
    path('signup/', authentication.views.signup, name='signup'),
    path('logout/', authentication.views.logout_user, name='logout'),
    path('', app.views.home, name='home'),
    path('ticket/add/', app.views.add_ticket, name='add_ticket'),
    path('ticket/<int:ticket_id>/delete/', app.views.delete_ticket, name='delete_ticket'),
    path('ticket/<int:ticket_id>/edit/', app.views.edit_ticket, name='edit_ticket'),
    path('flux/', app.views.flux, name='flux'),
    path('post/', app.views.post, name='post'),
    path('abonnement/', app.views.abonnement, name='abonnement'),
    path('abonnement/refresh/', app.views.refresh_abonnement, name='refresh_abonnement'),
    path('search_users/', app.views.search_users, name='search_users'),
    path('subscribe_user/', app.views.subscribe_user, name='subscribe_user'),
    path('add_review/', app.views.add_review, name='add_review'),
    path('search_tickets/', app.views.search_tickets, name='search_tickets'),
]
