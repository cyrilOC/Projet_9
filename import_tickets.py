#!/usr/bin/env python
"""
Script pour importer des tickets littéraires dans la base de données Django.
Usage: python import_tickets.py
"""
import os
import json
import django
import random
from datetime import timedelta, datetime

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litrevu.settings')
django.setup()

# Importe les modèles après avoir configuré Django
from django.contrib.auth import get_user_model
from app.models import Ticket
from django.utils import timezone

User = get_user_model()

def import_tickets(json_file='data_tickets_litteraires.json'):
    """Importe des tickets depuis un fichier JSON"""
    print(f"Lecture du fichier {json_file}...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            tickets_data = json.load(f)
    except FileNotFoundError:
        print(f"Erreur: Le fichier {json_file} n'existe pas.")
        return
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier {json_file} n'est pas un JSON valide.")
        return
    
    # Récupération des utilisateurs existants
    users = list(User.objects.all())
    if not users:
        print("Aucun utilisateur trouvé. Veuillez créer au moins un utilisateur.")
        return
    
    print(f"Importation de {len(tickets_data)} tickets...")
    
    # Dates de création réparties sur les 30 derniers jours
    now = timezone.now()
    
    tickets_created = 0
    for ticket_data in tickets_data:
        # Choix aléatoire d'un utilisateur
        user = random.choice(users)
        
        # Date aléatoire dans les 30 derniers jours
        days_ago = random.randint(0, 30)
        created_at = now - timedelta(days=days_ago, 
                                    hours=random.randint(0, 23), 
                                    minutes=random.randint(0, 59))
        
        # Création du ticket
        ticket = Ticket(
            title=ticket_data['title'],
            description=ticket_data['description'],
            user=user,
            status=ticket_data.get('status', 'open'),
            priority=ticket_data.get('priority', 'medium'),
            created_at=created_at,
            time_created=created_at  # Duplication pour compatibilité
        )
        ticket.save()
        tickets_created += 1
        
    print(f"{tickets_created} tickets ont été créés avec succès!")

if __name__ == '__main__':
    import_tickets()
    print("Terminé!")
