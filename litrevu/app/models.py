from django.db import models

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings



class Ticket(models.Model):
    # Your Ticket model definition goes here
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('open', 'Ouvert'), ('closed', 'Fermé')], default='open')
    priority = models.CharField(max_length=20, choices=[('low', 'Basse'), ('medium', 'Moyenne'), ('high', 'Haute')], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_reviews_count(self):
        """Renvoie le nombre total de critiques pour ce ticket."""
        return self.review_set.count()
    
    def get_average_rating(self):
        """Calcule et renvoie la note moyenne des critiques pour ce ticket."""
        reviews = self.review_set.all()
        if not reviews:
            return None
        total_rating = sum(review.rating for review in reviews)
        return round(total_rating / len(reviews), 1)  # Arrondi à 1 décimale


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    response = models.TextField(max_length=2048, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserFollows(models.Model):
    # Your UserFollows model definition goes here
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_by')
    follow_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = ('user', 'followed_user', )
