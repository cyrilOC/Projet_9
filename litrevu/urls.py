from django.urls import path, include
import app.views

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('ticket/add/', app.views.add_ticket, name='add_ticket'),
    path('ticket/<int:ticket_id>/delete/', app.views.delete_ticket, name='delete_ticket'),
    path('ticket/<int:ticket_id>/edit/', app.views.edit_ticket, name='edit_ticket'),
]