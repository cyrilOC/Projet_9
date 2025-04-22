from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Routes principales de l'application
    path('', views.home, name='home'),
    path('flux/', views.flux, name='flux'),
    path('user/<int:user_id>/flux/', views.user_flux, name='user_flux'),
    path('user/<int:user_id>/toggle_follow/', views.toggle_follow, name='toggle_follow'),
    path('ticket/<int:ticket_id>/flux/', views.ticket_flux, name='ticket_flux'),
    path('post/', views.post, name='post'),
    path('abonnement/', views.abonnement, name='abonnement'),
    
    # Routes d'API pour les recherches et actions dynamiques
    path('search_users/', views.search_users, name='search_users'),
    path('search_tickets/', views.search_tickets, name='search_tickets'),
    path('subscribe_user/', views.subscribe_user, name='subscribe_user'),
    path('abonnement/refresh/', views.refresh_abonnement, name='refresh_abonnement'),
    path('add_ticket/', views.add_ticket, name='add_ticket'),
    path('add_review/', views.add_review, name='add_review'),
    
    # Routes pour l'édition et suppression
    path('ticket/<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
    path('ticket/<int:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('create_review/<int:ticket_id>/', views.create_review_for_ticket, name='create_review_for_ticket'),
    
    # Routes d'authentification temporaires (jusqu'à ce que le module auth soit complètement implémenté)
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]