from django.shortcuts import get_object_or_404, redirect, render
from .models import Ticket, Review  # Ensure Review is imported
from .forms import TicketForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import json
from .models import UserFollows
from django.core.paginator import Paginator
from itertools import chain
from django.contrib.auth.decorators import login_required
from .models import UserBlocks  # Ajoutez cette importation

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
    # Récupérer les IDs des utilisateurs bloqués par l'utilisateur courant
    blocked_users = request.user.blocking.values_list('blocked_user_id', flat=True)
    # Récupérer les IDs des utilisateurs qui ont bloqué l'utilisateur courant
    users_blocking_me = request.user.blocked_by.values_list('user_id', flat=True)
    
    # Combiner les deux listes d'utilisateurs dont on veut filtrer le contenu
    excluded_users = list(blocked_users) + list(users_blocking_me)
    
    # Récupérer les tickets et critiques, en excluant ceux des utilisateurs bloqués ou qui nous ont bloqués
    tickets = Ticket.objects.filter(
        models.Q(user=request.user) |
        models.Q(user__in=request.user.following.values('followed_user'))
    ).exclude(user__id__in=excluded_users).order_by('-created_at')
    
    reviews = Review.objects.filter(
        models.Q(user=request.user) |
        models.Q(user__in=request.user.following.values('followed_user')) |
        models.Q(ticket__user=request.user)
    ).exclude(user__id__in=excluded_users).order_by('-created_at')
    
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

@login_required
def user_flux(request, user_id):
    """Affiche le flux propre à un utilisateur spécifique (ses tickets et reviews)"""
    User = get_user_model()
    target_user = get_object_or_404(User, id=user_id)
    
    # Vérifier si l'utilisateur est déjà suivi par l'utilisateur connecté
    is_followed = UserFollows.objects.filter(
        user=request.user, 
        followed_user=target_user
    ).exists()
    
    # Le reste du code reste inchangé
    tickets = Ticket.objects.filter(user=target_user).order_by('-created_at')
    reviews = Review.objects.filter(user=target_user).order_by('-created_at')
    feed_items = list(chain(tickets, reviews))
    feed_items.sort(key=lambda item: item.created_at, reverse=True)
    paginator = Paginator(feed_items, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'app/user_flux.html', {
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'paginator': paginator,
        'target_user': target_user,
        'is_followed': is_followed,
    })

@login_required
def ticket_flux(request, ticket_id):
    """Affiche un ticket spécifique avec toutes ses critiques en ordre chronologique"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Récupérer toutes les critiques liées à ce ticket, triées par date de création (du plus ancien au plus récent)
    reviews = Review.objects.filter(ticket=ticket).order_by('created_at')
    
    return render(request, 'app/ticket_flux.html', {
        'ticket': ticket,
        'reviews': reviews,
    })

@login_required
def toggle_follow(request, user_id):
    """Basculer entre s'abonner et se désabonner d'un utilisateur."""
    User = get_user_model()
    target_user = get_object_or_404(User, id=user_id)
    
    # Empêcher de s'abonner à soi-même
    if target_user == request.user:
        return redirect('user_flux', user_id=user_id)
    
    # Vérifier si l'utilisateur est déjà suivi
    existing_follow = UserFollows.objects.filter(
        user=request.user, 
        followed_user=target_user
    ).first()
    
    if existing_follow:
        # Se désabonner
        existing_follow.delete()
    else:
        # S'abonner
        UserFollows.objects.create(user=request.user, followed_user=target_user)
    
    # Rediriger vers la page de flux de l'utilisateur
    return redirect('user_flux', user_id=user_id)

@login_required
def search_results(request):
    """Affiche les résultats de recherche de tickets basés sur un mot-clé."""
    query = request.GET.get('q', '')
    
    if query:
        # Rechercher dans les titres et descriptions des tickets
        tickets = Ticket.objects.filter(
            models.Q(title__icontains=query) | 
            models.Q(description__icontains=query)
        ).order_by('-created_at')
    else:
        tickets = Ticket.objects.none()
    
    # Paginer les résultats (10 par page)
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'app/search_results.html', {
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'paginator': paginator,
        'query': query,
    })

def post(request):
    tickets = Ticket.objects.filter(user=request.user)
    message = None

    if request.method == 'POST':
        # Vérifier s'il s'agit d'une création de ticket
        if 'title' in request.POST:
            title = request.POST.get('title')
            description = request.POST.get('description')
            image = request.FILES.get('image')  # Récupérer l'image si elle existe
            create_review = request.POST.get('create_review') == 'yes'
            
            if title and description:
                # Créer le ticket
                new_ticket = Ticket.objects.create(
                    title=title,
                    description=description,
                    image=image,
                    user=request.user
                )
                
                # Si l'option de créer une critique est sélectionnée
                if create_review and 'headline' in request.POST:
                    headline = request.POST.get('headline')
                    body = request.POST.get('body')
                    rating = request.POST.get('rating')
                    
                    if headline and body and rating:
                        Review.objects.create(
                            ticket=new_ticket,
                            headline=headline,
                            body=body,
                            rating=rating,
                            user=request.user
                        )
                        message = f"Le ticket '{title}' et votre critique ont été créés."
                    else:
                        message = f"Le ticket '{title}' a été créé, mais la critique n'a pas pu être ajoutée."
                else:
                    message = f"Le ticket '{title}' a été créé."
                    
                # Rediriger vers le flux après la création
                return redirect('flux')
                
        # Traitement des critiques séparées (ancien code)
        elif 'headline' in request.POST and 'selected_ticket' in request.POST:
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
    blocked_users = [relation.blocked_user for relation in request.user.blocking.all()]
    
    return render(request, 'app/abonnement.html', {
        'followers': followers, 
        'following': following,
        'blocked_users': blocked_users
    })

def search_users(request):owing.values_list('followed_user_id', flat=True)
    query = request.GET.get('q', '')('blocked_user_id', flat=True)
    User = get_user_model()
    # Ensure the query filters correctly and excludes the current userts = [
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
            'username': user.username,       'id': user.id,
            'is_followed': user.id in followed_users,        'username': user.username,
            'is_blocked': user.id in blocked_users
        }r.id in blocked_users
        for user in users
    ]    for user in users
    
    # Handle cases where no users are found or the query is empty    
    if not results and query: cases where no users are found or the query is empty
        results = [{'id': -1, 'username': 'Aucun utilisateur trouvé', 'is_followed': False, 'is_blocked': False}]:
    sername': 'Aucun utilisateur trouvé', 'is_followed': False, 'is_blocked': False}]
    return JsonResponse(results, safe=False)
=False)
@csrf_exempt
def subscribe_user(request):@csrf_exempt
    if request.method == 'POST':quest):        if subscribe:
        data = json.loads(request.body)':scription
        user_id = data.get('user_id')=user_id)
        subscribe = data.get('subscribe')id = data.get('user_id')
id') Remove subscription
        if subscribe:delete()
            # Add subscription
            UserFollows.objects.get_or_create(user=request.user, followed_user_id=user_id)'status': 'success'})
        else:            # Add subscription
            # Remove subscriptiond_user_id=user_id)    return JsonResponse({'error': 'Invalid request method'}, status=400)
            UserFollows.objects.filter(user=request.user, followed_user_id=user_id).delete()        else:
ndef refresh_abonnement(request):
        return JsonResponse({'status': 'success'})er.username} for relation in request.user.followed_by.all()]

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def refresh_abonnement(request):sonResponse({'error': 'Invalid request method'}, status=400)@csrf_exempt
    followers = [{'username': relation.user.username} for relation in request.user.followed_by.all()]
    following = [{'username': relation.followed_user.username} for relation in request.user.following.all()] 'POST':
    return JsonResponse({'followers': followers, 'following': following})r relation in request.user.followed_by.all()]OST.get('ticket_search')
_user.username} for relation in request.user.following.all()]
@csrf_exemptollowers, 'following': following})
def add_review(request):
    if request.method == 'POST':@csrf_exempt
        ticket_title = request.POST.get('ticket_search')ew(request):        try:
        headline = request.POST.get('headline'), user=request.user)
        body = request.POST.get('body')
        rating = request.POST.get('rating')
dy')
        try:tus=404)
            ticket = Ticket.objects.get(title=ticket_title, user=request.user)
            Review.objects.create(ticket=ticket, headline=headline, body=body, rating=rating, user=request.user) status=400)
            return JsonResponse({'status': 'success'})            ticket = Ticket.objects.get(title=ticket_title, user=request.user)
        except Ticket.DoesNotExist:reate(ticket=ticket, headline=headline, body=body, rating=rating, user=request.user)def search_tickets(request):
            return JsonResponse({'error': 'Ticket not found'}, status=404)atus': 'success'})'q', '')

    return JsonResponse({'error': 'Invalid request'}, status=400)'}, status=404)ns=query)

def search_tickets(request):n JsonResponse({'error': 'Invalid request'}, status=400)
    query = request.GET.get('q', '')
    # Correction de la syntaxe du filtre icontains
    tickets = Ticket.objects.filter(title__icontains=query)n,
    results = [ icontains
        {s = Ticket.objects.filter(title__icontains=query)
            'id': ticket.id, ckets
            'title': ticket.title,   {
            'description': ticket.description,        'id': ticket.id, 
            'user': ticket.user.usernamet si aucun ticket n'est trouvé
        } cket.description,
        for ticket in ticketsuser': ''}]
    ]
    r': ''}]
    # Retourner un message par défaut si aucun ticket n'est trouvé
    if not results and query:
        results = [{'id': -1, 'title': 'Aucun ticket trouvé', 'description': '', 'user': ''}]    # Retourner un message par défaut si aucun ticket n'est trouvé
    elif not results:lts and query:@login_required
        results = [{'id': -1, 'title': 'Commencez à taper pour rechercher', 'description': '', 'user': ''}]': 'Aucun ticket trouvé', 'description': '', 'user': ''}](request, review_id):
        
    return JsonResponse(results, safe=False)    results = [{'id': -1, 'title': 'Commencez à taper pour rechercher', 'description': '', 'user': ''}]
ST':
@login_required('headline')
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    _review(request, review_id):
    if request.method == 'POST':d=review_id, user=request.user)if headline and body and rating:
        headline = request.POST.get('headline')
        body = request.POST.get('body')':
        rating = request.POST.get('rating')t('headline')ting
        ST.get('body')
        if headline and body and rating:rating')ct('flux')
            review.headline = headline    
            review.body = bodyit_review.html', {'review': review})
            review.rating = rating            review.headline = headline
            review.save()iew.body = body@login_required
            return redirect('flux')equest, ticket_id):
    
    return render(request, 'app/edit_review.html', {'review': review})        return redirect('flux')

@login_required
def create_review_for_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Vérifier si l'utilisateur a déjà créé une critique pour ce ticketticket = get_object_or_404(Ticket, id=ticket_id)
    existing_review = Review.objects.filter(user=request.user, ticket=ticket).first()
    if (existing_review): critique pour ce ticketget('headline')
        # Rediriger vers l'édition de la critique existantelter(user=request.user, ticket=ticket).first()
        return redirect('edit_review', review_id=existing_review.id)
    # Rediriger vers l'édition de la critique existante
    if request.method == 'POST':eview_id=existing_review.id)if headline and body and rating:
        headline = request.POST.get('headline')
        body = request.POST.get('body')':
        rating = request.POST.get('rating')t('headline')ser,
        ody')
        if headline and body and rating:OST.get('rating')
            Review.objects.create(
                ticket=ticket,adline and body and rating:
                user=request.user,turn redirect('flux')
                headline=headline,            ticket=ticket,
                body=body,iew.html', {'ticket': ticket})
                rating=rating                headline=headline,
            )    body=body,@csrf_exempt
            return redirect('flux')atinger(request):
    
    return render(request, 'app/create_review.html', {'ticket': ticket})x')

@csrf_exempte_review.html', {'ticket': ticket})
def block_user(request):
    """Gérer le blocage/déblocage d'utilisateurs"""@csrf_exempt
    if request.method == 'POST':quest):        if block:
        data = json.loads(request.body)e d'utilisateurs"""uter le blocage
        user_id = data.get('user_id')
        block = data.get('block')

        if block: = data.get('block')
            # Ajouter le blocage
            UserBlocks.objects.get_or_create(user=request.user, blocked_user_id=user_id)
            # Si l'utilisateur est abonné à cet utilisateur, le désabonner automatiquement            # Ajouter le blocage
            UserFollows.objects.filter(user=request.user, followed_user_id=user_id).delete()request.user, blocked_user_id=user_id)        return JsonResponse({'status': 'success'})
        else:er automatiquement method'}, status=400)            UserFollows.objects.filter(user=request.user, followed_user_id=user_id).delete()        else:





    return JsonResponse({'error': 'Invalid request method'}, status=400)        return JsonResponse({'status': 'success'})            UserBlocks.objects.filter(user=request.user, blocked_user_id=user_id).delete()            # Supprimer le blocage            # Supprimer le blocage
            UserBlocks.objects.filter(user=request.user, blocked_user_id=user_id).delete()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)