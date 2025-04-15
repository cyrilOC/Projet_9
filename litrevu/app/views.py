from django.shortcuts import get_object_or_404, redirect, render
from .models import Ticket
from .forms import TicketForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserFollows

def home(request):
    return render(request, 'app/home.html')

@csrf_exempt
def add_ticket(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Ticket.objects.create(title=title, user=request.user)
            return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    if request.method == 'POST':
        ticket.delete()
        return redirect('home')
    return render(request, 'app/delete_ticket.html', {'ticket': ticket})

def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'app/edit_ticket.html', {'form': form, 'ticket': ticket})

def flux(request):
    return render(request, 'app/flux.html')

def post(request):
    return render(request, 'app/post.html')

def abonnement(request):
    followers = [relation.user for relation in request.user.followed_by.all()]
    following = [relation.followed_user for relation in request.user.following.all()]
    return render(request, 'app/abonnement.html', {'followers': followers, 'following': following})

def search_users(request):
    query = request.GET.get('q', '')
    User = get_user_model()
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    followed_users = request.user.following.values_list('followed_user_id', flat=True)
    results = [
        {
            'id': user.id,
            'username': user.username,
            'is_followed': user.id in followed_users
        }
        for user in users
    ]
    return JsonResponse(results, safe=False)

@csrf_exempt
def subscribe_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        subscribe = data.get('subscribe')

        if subscribe:
            # Add subscription
            UserFollows.objects.get_or_create(user=request.user, followed_user_id=user_id)
        else:
            # Remove subscription
            UserFollows.objects.filter(user=request.user, followed_user_id=user_id).delete()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def refresh_abonnement(request):
    followers = [{'username': relation.user.username} for relation in request.user.followed_by.all()]
    following = [{'username': relation.followed_user.username} for relation in request.user.following.all()]
    return JsonResponse({'followers': followers, 'following': following})

@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        ticket_title = request.POST.get('ticket_search')
        headline = request.POST.get('headline')
        body = request.POST.get('body')
        rating = request.POST.get('rating')

        try:
            ticket = Ticket.objects.get(title=ticket_title, user=request.user)
            Review.objects.create(ticket=ticket, headline=headline, body=body, rating=rating, user=request.user)
            return JsonResponse({'status': 'success'})
        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def search_tickets(request):
    query = request.GET.get('q', '')
    tickets = Ticket.objects.filter(title__icontains=query, user=request.user)
    results = [{'id': ticket.id, 'title': ticket.title} for ticket in tickets]
    return JsonResponse(results, safe=False)