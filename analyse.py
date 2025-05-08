import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
import uuid

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GIN_backend.settings')
django.setup()

# Import des modèles après l'initialisation de Django
from django.contrib.auth.models import Permission, Group, ContentType
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from gin.models import Formation as GinFormation, Service
from inscription.models import Utilisateur, Formation, Inscription, RechercheFormation
from stages.models import StageOffer, StageApplication
from accounts.models import Department, User, UserProfile
from partenaires.models import Partenaire
from realisations.models import Realisation
from contacts.models import ContactMessage, ContactReponse

# Fonction pour générer des dates aléatoires
def random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

# Fonction pour créer un fichier temporaire pour les uploads
def create_temp_file(name, content):
    file = ContentFile(content)
    file.name = name
    return file

def safe_get_or_create(model, **kwargs):
    """Fonction sécurisée pour get_or_create qui gère les erreurs d'intégrité"""
    try:
        instance, created = model.objects.get_or_create(**kwargs)
        return instance, created
    except model.MultipleObjectsReturned:
        # Si plusieurs objets correspondent à la requête, on en prend un
        print(f"ATTENTION: Plusieurs objets {model.__name__} trouvés avec {kwargs}")
        return model.objects.filter(**kwargs).first(), False
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            # Si contrainte d'unicité violée, on récupère l'objet existant
            print(f"ATTENTION: Contrainte d'unicité sur {model.__name__} avec {kwargs}")
            # Trouver la clé qui pose problème (généralement le premier champ unique)
            fields = [f for f in kwargs if f != 'defaults']
            if fields:
                filters = {k: kwargs[k] for k in fields}
                return model.objects.filter(**filters).first(), False
        # Autres erreurs
        print(f"ERREUR lors de la création de {model.__name__}: {str(e)}")
        raise

@transaction.atomic
def populate_database():
    print("Début de la population de la base de données...")

    # 1. ContentType (requis avant d'autres tables)
    print("Population des ContentTypes...")
    # Les ContentTypes sont généralement créés automatiquement par Django
    # Pas besoin de les créer manuellement

    # 2. Permission
    print("Population des Permissions...")
    # Les permissions sont généralement créées automatiquement par Django
    # On peut éventuellement en ajouter des spécifiques

    # 3. Group
    print("Population des Groups...")
    groups = [
        safe_get_or_create(Group, name="Administrateurs")[0],
        safe_get_or_create(Group, name="Formateurs")[0],
        safe_get_or_create(Group, name="Étudiants")[0],
        safe_get_or_create(Group, name="Responsables RH")[0],
    ]

    # Assignation des permissions aux groupes
    all_perms = Permission.objects.all()
    admin_perms = all_perms
    formateur_perms = Permission.objects.filter(codename__contains='formation')
    etudiant_perms = Permission.objects.filter(codename__startswith='view')
    rh_perms = Permission.objects.filter(codename__contains='stage')

    groups[0].permissions.set(admin_perms)
    groups[1].permissions.set(formateur_perms)
    groups[2].permissions.set(etudiant_perms)
    groups[3].permissions.set(rh_perms)

    # 4. Department
    print("Population des Departments...")
    departments = [
        safe_get_or_create(
            Department,
            name="Direction", 
            defaults={'description': "Département de direction de l'entreprise"}
        )[0],
        safe_get_or_create(
            Department,
            name="Formation", 
            defaults={'description': "Département en charge des formations"}
        )[0],
        safe_get_or_create(
            Department,
            name="Développement", 
            defaults={'description': "Département de développement logiciel"}
        )[0],
        safe_get_or_create(
            Department,
            name="Marketing", 
            defaults={'description': "Département marketing et communication"}
        )[0],
        safe_get_or_create(
            Department,
            name="Ressources Humaines", 
            defaults={'description': "Département des ressources humaines"}
        )[0],
    ]

    # 5. User
    print("Population des Users...")
    users = []
    
    # Admin
    admin_user = safe_get_or_create(
        User,
        email="admin@gin.com",
        defaults={
            'first_name': "Admin",
            'last_name': "System",
            'role': "Administrateur",
            'department': departments[0],
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'date_joined': timezone.now()
        }
    )[0]
    admin_user.set_password("admin123")
    admin_user.save()
    try:
        admin_user.groups.add(groups[0])
    except Exception as e:
        print(f"Impossible d'ajouter le groupe à l'utilisateur admin: {str(e)}")
    users.append(admin_user)
    
    # Autres utilisateurs
    user_data = [
        {
            'email': "formateur@gin.com", 'password': "form123",
            'first_name': "Jean", 'last_name': "Dupont",
            'role': "Formateur", 'department': departments[1],
            'group': groups[1]
        },
        {
            'email': "dev@gin.com", 'password': "dev123",
            'first_name': "Marie", 'last_name': "Laurent",
            'role': "Développeur", 'department': departments[2],
            'group': groups[2]
        },
        {
            'email': "marketing@gin.com", 'password': "mark123",
            'first_name': "Sophie", 'last_name': "Martin",
            'role': "Marketeur", 'department': departments[3],
            'group': groups[2]
        },
        {
            'email': "rh@gin.com", 'password': "rh123",
            'first_name': "Pierre", 'last_name': "Dubois",
            'role': "RH", 'department': departments[4],
            'group': groups[3]
        },
    ]
    
    for data in user_data:
        try:
            user = safe_get_or_create(
                User,
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'department': data['department'],
                    'is_staff': True,
                    'is_active': True,
                    'date_joined': timezone.now() - timedelta(days=random.randint(1, 365))
                }
            )[0]
            user.set_password(data['password'])
            user.save()
            try:
                user.groups.add(data['group'])
            except Exception as e:
                print(f"Impossible d'ajouter le groupe à l'utilisateur {data['email']}: {str(e)}")
            users.append(user)
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur {data['email']}: {str(e)}")
            continue
    
    # 6. UserProfile
    print("Population des UserProfiles...")
    for user in users:
        try:
            safe_get_or_create(
                UserProfile,
                user=user,
                defaults={
                    'bio': f"Biographie professionnelle de {user.first_name} {user.last_name}",
                    'phone_number': f"06{random.randint(10000000, 99999999)}",
                    'position': user.role
                }
            )
        except Exception as e:
            print(f"Erreur lors de la création du profil pour {user.email}: {str(e)}")
            continue

    # 7. Utilisateur (inscription_utilisateur)
    print("Population des Utilisateurs...")
    for user in users:
        try:
            safe_get_or_create(
                Utilisateur,
                user=user,
                defaults={
                    'telephone': f"06{random.randint(10000000, 99999999)}",
                    'adresse': f"{random.randint(1, 100)} rue des {random.choice(['Lilas', 'Roses', 'Tulipes', 'Orchidées'])}",
                    'date_naissance': random_date(datetime(1970, 1, 1), datetime(2000, 1, 1)).date(),
                    'created_at': timezone.now(),
                    'updated_at': timezone.now()
                }
            )
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur d'inscription pour {user.email}: {str(e)}")
            continue

    # 8. Service
    print("Population des Services...")
    services = []
    service_data = [
        {
            'nom': "Développement Web",
            'description': "Création de sites web professionnels et d'applications web sur mesure"
        },
        {
            'nom': "Formation Informatique",
            'description': "Formations professionnelles en développement, administration système et cybersécurité"
        },
        {
            'nom': "Conseil IT",
            'description': "Services de conseil en stratégie informatique et transformation digitale"
        },
        {
            'nom': "Audit de Sécurité",
            'description': "Audit complet de sécurité informatique avec recommandations"
        },
        {
            'nom': "Maintenance Informatique",
            'description': "Services de maintenance préventive et corrective pour vos systèmes"
        },
    ]
    
    for data in service_data:
        try:
            service = safe_get_or_create(
                Service,
                nom=data['nom'],
                defaults={'description': data['description']}
            )[0]
            services.append(service)
        except Exception as e:
            print(f"Erreur lors de la création du service {data['nom']}: {str(e)}")
            continue

    # 9. GinFormation
    print("Population des Formations (gin_formation)...")
    for i in range(1, 6):
        try:
            start_date = random_date(datetime.now().date(), (datetime.now() + timedelta(days=180)).date())
            end_date = start_date + timedelta(days=random.randint(2, 30))
            
            safe_get_or_create(
                GinFormation,
                titre=f"Formation {i}",
                defaults={
                    'description': f"Description détaillée de la formation {i}",
                    'date_debut': start_date,
                    'date_fin': end_date,
                    'lieu': random.choice(["Paris", "Lyon", "Marseille", "Bordeaux", "Lille"])
                }
            )
        except Exception as e:
            print(f"Erreur lors de la création de la formation GIN {i}: {str(e)}")
            continue

    # 10. Formation (inscription_formation)
    print("Population des Formations (inscription_formation)...")
    formations = []
    for i in range(1, 11):
        try:
            formation = safe_get_or_create(
                Formation,
                titre=f"Formation Professionnelle {i}",
                defaults={
                    'description': f"Description détaillée de la formation professionnelle {i}",
                    'duree': f"{random.randint(1, 5)} jours",
                    'prerequis': f"Prérequis pour la formation {i}",
                    'objectifs': f"Objectifs pédagogiques de la formation {i}",
                    'date_session': random_date(datetime.now().date(), (datetime.now() + timedelta(days=180)).date()),
                    'lieu': random.choice(["Paris", "Lyon", "Marseille", "Bordeaux", "Lille"]),
                    'capacite': random.randint(10, 30),
                    'department': random.choice(departments),
                    'statut': random.choice(["Ouverte", "Complète", "Annulée", "En attente"]),
                    'created_by': random.choice(users),
                    'created_at': timezone.now() - timedelta(days=random.randint(10, 100)),
                    'updated_at': timezone.now()
                }
            )[0]
            formations.append(formation)
        except Exception as e:
            print(f"Erreur lors de la création de la formation d'inscription {i}: {str(e)}")
            continue

    # 11. Inscription
    print("Population des Inscriptions...")
    for formation in formations:
        if not formation:
            continue
            
        for _ in range(random.randint(3, 10)):
            try:
                # Certaines inscriptions avec des utilisateurs existants, d'autres sans
                user = random.choice([None] + users) if random.random() > 0.5 else None
                
                prenom = random.choice(["Thomas", "Julie", "Alexandre", "Emma", "Lucas", "Chloé"]) if not user else user.first_name
                nom = random.choice(["Dupont", "Martin", "Bernard", "Petit", "Durand"]) if not user else user.last_name
                email = f"{prenom.lower()}.{nom.lower()}@example.com" if not user else user.email
                
                # Utilisons un tracking_code unique pour être sûr
                tracking_code = str(uuid.uuid4())[:8]
                
                safe_get_or_create(
                    Inscription,
                    formation=formation,
                    email=email,
                    tracking_code=tracking_code,  # Ajout du tracking_code dans les critères de recherche
                    defaults={
                        'user': user,
                        'nom': nom,
                        'prenom': prenom,
                        'telephone': f"06{random.randint(10000000, 99999999)}",
                        'commentaire': f"Commentaire de {prenom} {nom}" if random.random() > 0.5 else "",
                        'statut': random.choice(["En attente", "Confirmée", "Annulée", "Terminée"]),
                        'date_inscription': timezone.now() - timedelta(days=random.randint(1, 60)),
                        'date_modification': timezone.now() - timedelta(days=random.randint(0, 30))
                    }
                )
            except Exception as e:
                print(f"Erreur lors de la création d'une inscription: {str(e)}")
                continue

    # 12. RechercheFormation
    print("Population des RecherchesFormation...")
    utilisateurs = list(Utilisateur.objects.all())
    termes_recherche = ["Python", "Java", "Web", "Sécurité", "Cloud", "DevOps", "Management", "Certification"]
    
    if not utilisateurs:
        print("Aucun utilisateur trouvé pour créer des recherches de formation")
    else:
        for utilisateur in utilisateurs:
            for _ in range(random.randint(1, 5)):
                try:
                    date_recherche = timezone.now() - timedelta(days=random.randint(1, 30))
                    terme = random.choice(termes_recherche)
                    
                    safe_get_or_create(
                        RechercheFormation,
                        utilisateur=utilisateur,
                        terme_recherche=terme,
                        date_recherche=date_recherche  # Utilisation de la date comme identifiant supplémentaire
                    )
                except Exception as e:
                    print(f"Erreur lors de la création d'une recherche de formation: {str(e)}")
                    continue

    # 13. StageOffer
    print("Population des StageOffers...")
    stage_offers = []
    stage_titles = ["Développement Web", "Développement Mobile", "Data Science", "Design UX/UI", "Marketing Digital"]
    
    for i in range(1, 11):
        title = random.choice(stage_titles) + f" - Offre {i}"
        
        stage_offer = StageOffer.objects.get_or_create(
            title=title,
            defaults={
                'department': random.choice(departments),
                'description': f"Description détaillée du stage {title}",
                'missions': f"Missions principales: \n- Mission 1\n- Mission 2\n- Mission 3",
                'required_skills': f"Compétences requises: \n- Compétence 1\n- Compétence 2\n- Compétence 3",
                'start_date': random_date(datetime.now().date(), (datetime.now() + timedelta(days=180)).date()),
                'duration': f"{random.randint(2, 6)} mois",
                'stage_type': random.choice(["Stage", "Alternance", "Stage de fin d'études"]),
                'status': random.choice(["Ouverte", "Pourvue", "Clôturée"]),
                'created_by': random.choice(users),
                'created_at': timezone.now() - timedelta(days=random.randint(10, 100)),
                'updated_at': timezone.now()
            }
        )[0]
        stage_offers.append(stage_offer)

    # 14. StageApplication
    print("Population des StageApplications...")
    prenoms = ["Thomas", "Julie", "Alexandre", "Emma", "Lucas", "Chloé", "Mathieu", "Léa", "Nicolas", "Sarah"]
    noms = ["Dupont", "Martin", "Bernard", "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Michel"]
    
    for stage_offer in stage_offers:
        for _ in range(random.randint(2, 8)):
            prenom = random.choice(prenoms)
            nom = random.choice(noms)
            
            # Création d'un contenu fictif pour les fichiers
            cv_content = f"CV de {prenom} {nom}".encode('utf-8')
            letter_content = f"Lettre de motivation de {prenom} {nom}".encode('utf-8')
            
            StageApplication.objects.get_or_create(
                stage_offer=stage_offer,
                email=f"{prenom.lower()}.{nom.lower()}@example.com",
                defaults={
                    'first_name': prenom,
                    'last_name': nom,
                    'phone': f"06{random.randint(10000000, 99999999)}",
                    'cv': create_temp_file(f"cv_{prenom}_{nom}.pdf", cv_content),
                    'motivation_letter': create_temp_file(f"lettre_{prenom}_{nom}.pdf", letter_content),
                    'tracking_code': str(uuid.uuid4())[:8],
                    'status': random.choice(["Reçue", "En cours d'examen", "Entretien planifié", "Acceptée", "Refusée"]),
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 60)),
                    'updated_at': timezone.now() - timedelta(days=random.randint(0, 30))
                }
            )

    # 15. Partenaire
    print("Population des Partenaires...")
    partenaires = [
        "Microsoft", "Google", "Amazon Web Services", "Oracle", "IBM", 
        "Cisco", "SAP", "Salesforce", "Adobe", "Dell"
    ]
    
    for partenaire in partenaires:
        Partenaire.objects.get_or_create(
            nom=partenaire,
            defaults={
                'site_web': f"https://www.{partenaire.lower().replace(' ', '')}.com"
            }
        )

    # 16. Realisation
    print("Population des Realisations...")
    projets = [
        "Refonte site web", "Application mobile", "Système ERP", 
        "Plateforme e-learning", "Infrastructure cloud"
    ]
    entreprises = [
        "Entreprise A", "Société B", "Compagnie C", "Groupe D", "Startup E"
    ]
    
    for _ in range(10):
        Realisation.objects.get_or_create(
            projet=random.choice(projets) + f" - {random.choice(['V1', 'V2', 'V3'])}",
            entreprise=random.choice(entreprises),
            defaults={
                'avis': f"Très satisfait de la prestation. Équipe professionnelle et à l'écoute.",
                'type_personne': random.choice(["Client", "Partenaire", "Employé"])
            }
        )

    # 17. ContactMessage
    print("Population des ContactMessages...")
    sujets = [
        "Demande d'information", "Demande de devis", "Réclamation", 
        "Proposition de partenariat", "Question technique"
    ]
    
    contact_messages = []
    for i in range(20):
        prenom = random.choice(prenoms)
        nom = random.choice(noms)
        
        message = ContactMessage.objects.get_or_create(
            email=f"{prenom.lower()}.{nom.lower()}@example.com",
            defaults={
                'nom': nom,
                'prenom': prenom,
                'telephone': f"06{random.randint(10000000, 99999999)}",
                'sujet': random.choice(sujets),
                'message': f"Contenu du message de {prenom} {nom}. Lorem ipsum dolor sit amet...",
                'departement_destinataire': random.choice(departments) if random.random() > 0.3 else None,
                'statut': random.choice(["Nouveau", "En cours de traitement", "Traité", "Archivé"]),
                'date_creation': timezone.now() - timedelta(days=random.randint(1, 60)),
                'date_modification': timezone.now() - timedelta(days=random.randint(0, 30))
            }
        )[0]
        contact_messages.append(message)

    # 18. ContactReponse
    print("Population des ContactReponses...")
    for message in contact_messages:
        # Seulement certains messages ont une réponse
        if random.random() > 0.3:
            ContactReponse.objects.get_or_create(
                message_original=message,
                defaults={
                    'reponse': f"Réponse au message de {message.prenom} {message.nom}. Lorem ipsum dolor sit amet...",
                    'repondant': random.choice(users) if random.random() > 0.2 else None,
                    'date_reponse': message.date_creation + timedelta(days=random.randint(1, 10))
                }
            )

    # 19. LogEntry (django_admin_log)
    print("Population des LogEntries...")
    # Les LogEntry sont généralement créés automatiquement lors des actions dans l'admin
    # On pourrait en créer artificiellement mais c'est rarement nécessaire

    # 20. Session (django_session)
    print("Population des Sessions...")
    # Les sessions sont généralement créées automatiquement
    # On pourrait en créer artificiellement mais c'est rarement nécessaire

    print("Population de la base de données terminée avec succès!")

def main():
    """Fonction principale avec gestion d'exceptions globale"""
    try:
        populate_database()
    except Exception as e:
        print(f"\nERREUR GLOBALE: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nLe script a rencontré une erreur mais certaines données ont peut-être été insérées correctement.")

if __name__ == "__main__":
    main()