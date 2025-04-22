from django import template
from app.models import Ticket, Review
from django.utils import timezone
from django.db.models import Avg

register = template.Library()

@register.simple_tag
def user_tickets_count(user):
    """Renvoie le nombre de tickets créés par l'utilisateur."""
    return Ticket.objects.filter(user=user).count()

@register.simple_tag
def user_reviews_count(user):
    """Renvoie le nombre de critiques créées par l'utilisateur."""
    return Review.objects.filter(user=user).count()

@register.simple_tag
def user_average_rating(user):
    """Renvoie la note moyenne des critiques faites par l'utilisateur."""
    avg = Review.objects.filter(user=user).aggregate(Avg('rating'))['rating__avg']
    if avg is not None:
        return round(avg, 1)
    return "N/A"

@register.simple_tag
def user_last_activity(user):
    """Renvoie la date de la dernière activité (ticket ou critique) de l'utilisateur."""
    latest_ticket = Ticket.objects.filter(user=user).order_by('-created_at').first()
    latest_review = Review.objects.filter(user=user).order_by('-created_at').first()
    
    latest_dates = []
    if latest_ticket:
        latest_dates.append(latest_ticket.created_at)
    if latest_review:
        latest_dates.append(latest_review.created_at)
    
    if latest_dates:
        return max(latest_dates)
    return None

@register.filter
def time_since(date):
    """Renvoie le temps écoulé depuis une date donnée en format lisible."""
    if not date:
        return "Jamais"
        
    now = timezone.now()
    diff = now - date
    
    seconds = diff.total_seconds()
    if seconds < 60:
        return "il y a quelques secondes"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"il y a {hours} heure{'s' if hours > 1 else ''}"
    elif seconds < 2592000:  # 30 jours
        days = int(seconds // 86400)
        return f"il y a {days} jour{'s' if days > 1 else ''}"
    elif seconds < 31536000:  # 365 jours
        months = int(seconds // 2592000)
        return f"il y a {months} mois"
    else:
        years = int(seconds // 31536000)
        return f"il y a {years} an{'s' if years > 1 else ''}"