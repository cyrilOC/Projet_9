from django.shortcuts import get_object_or_404, redirect, render
from .models import Ticket, Review  # Ensure Review is imported
from .forms import TicketForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserFollows
from django.core.paginator import Paginator
from itertools import chain
from django.contrib.auth.decorators import login_required

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

@login_required
def flux(request):
    # Récupérer l'utilisateur connecté
    user = request.user
    
    # Récupérer la liste des utilisateurs suivis
    followed_users = [relation.followed_user for relation in user.following.all()]
    
    # Inclure l'utilisateur actuel dans la liste pour voir également ses propres posts
    users_to_display = [user] + followed_users
    
    # Récupérer les tickets créés par l'utilisateur et les utilisateurs suivis
    tickets = Ticket.objects.filter(user__in=users_to_display).order_by('-created_at')
    
    # Récupérer les reviews créées par l'utilisateur et les utilisateurs suivis
    reviews = Review.objects.filter(user__in=users_to_display).order_by('-created_at')
    
    # Combiner les tickets et les reviews dans une seule liste
    feed_items = list(chain(tickets, reviews))
    
    # Trier la liste par date de création (du plus récent au plus ancien)
    feed_items.sort(key=lambda item: item.created_at, reverse=True)
    
    # Paginer les résultats (10 par page)
    paginator = Paginator(feed_items, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'app/flux.html', {
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'paginator': paginator,
    })

def post(request):
    tickets = Ticket.objects.filter(user=request.user)
    message = None

    if request.method == 'POST' and 'title' in request.POST:
        title = request.POST.get('title')
        description = request.POST.get('description')
        if title and description:
            Ticket.objects.create(title=title, description=description, user=request.user)
            message = f"Le ticket '{title}' a été créé."

    if request.method == 'POST' and 'headline' in request.POST:
        ticket_id = request.POST.get('selected_ticket')
        headline = request.POST.get('headline')
        body = request.POST.get('body')
        rating = request.POST.get('rating')

        try:
            ticket = Ticket.objects.get(id=ticket_id)
            Review.objects.create(ticket=ticket, headline=headline, body=body, rating=rating, user=request.user)
            message = "Votre critique a été créée."
        except Ticket.DoesNotExist:
            message = "Le ticket sélectionné n'existe pas."

    return render(request, 'app/post.html', {'tickets': tickets, 'message': message})

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
    
    # Ajout d'un message par défaut si aucun résultat n'est trouvé
    if not results and query:
        results = [{'id': -1, 'username': 'Aucun utilisateur trouvé', 'is_followed': False}]
    elif not results:
        results = [{'id': -1, 'username': 'Commencez à taper pour rechercher', 'is_followed': False}]
        
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
    # Retirer la restriction user=request.user pour permettre de rechercher tous les tickets
    tickets = Ticket.objects.filter(title__icontains=query)
    results = [
        {
            'id': ticket.id, 
            'title': ticket.title,
            'description': ticket.description,
            'user': ticket.user.username
        } 
        for ticket in tickets
    ]
    
    # Retourner un message par défaut si aucun ticket n'est trouvé
    if not results and query:
        results = [{'id': -1, 'title': 'Aucun ticket trouvé', 'description': '', 'user': ''}]
    elif not results:
        results = [{'id': -1, 'title': 'Commencez à taper pour rechercher', 'description': '', 'user': ''}]
        
    return JsonResponse(results, safe=False)