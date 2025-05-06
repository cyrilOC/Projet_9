from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Create your models here.

def user_profile_path(instance, filename):
    # Utiliser un chemin relatif qui sera accessible via l'URL du serveur
    # Pas de répertoire media intermédiaire
    return f'profile_pictures/{instance.username}_{filename}'

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    # Add any additional fields you want here
    # For example, you can add a profile picture field
    CREATOR = 'CREATOR'
    SUBSCRIBER = 'SUBSCRIBER'

    ROLE_CHOICES = (
        (CREATOR, 'Créateur'),
        (SUBSCRIBER, 'Abonné'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name='Role')
    profile_picture = models.ImageField(upload_to=user_profile_path, blank=True, null=True, verbose_name='Photo de profil')
    presentation = models.TextField(blank=True, null=True, verbose_name='Présentation')
    
    @property
    def profile_picture_url(self):
        """Retourne l'URL complète de l'image de profil."""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            # S'assurer que l'URL est absolue et accessible directement
            return self.profile_picture.url
        return None