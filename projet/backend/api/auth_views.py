"""
Vues pour l'authentification et gestion des sessions
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from .models import User


class RegisterView(APIView):
    """
    Vue pour l'inscription des utilisateurs
    """
    permission_classes = (AllowAny,)
    authentication_classes = ()
    
    def post(self, request):
        """
        Inscription d'un nouvel utilisateur
        """
        try:
            data = request.data
            print(f"[DEBUG] Tentative d'inscription avec les données: {data}")
            
            # Vérifications des champs obligatoires
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not username:
                print("[DEBUG] Nom d'utilisateur manquant")
                return Response({
                    'error': 'Le nom d\'utilisateur est obligatoire'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not email:
                print("[DEBUG] Email manquant")
                return Response({
                    'error': 'L\'email est obligatoire'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            if not password or len(password) < 6:
                print("[DEBUG] Mot de passe invalide")
                return Response({
                    'error': 'Le mot de passe doit contenir au moins 6 caractères'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier que l'email n'existe pas déjà
            if User.objects.filter(email=email).exists():
                print(f"[DEBUG] Email {email} existe déjà")
                return Response({
                    'error': 'Un utilisateur avec cet email existe déjà'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Vérifier que le nom d'utilisateur n'existe pas déjà
            if User.objects.filter(username=username).exists():
                print(f"[DEBUG] Username {username} existe déjà")
                return Response({
                    'error': 'Ce nom d\'utilisateur est déjà pris'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"[DEBUG] Création de l'utilisateur {username} avec email {email}")
            
            # Récupérer la ville depuis le frontend (priorité au champ 'ville', puis 'city')
            ville = data.get('ville', '') or data.get('city', '')
            
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=data.get('role', 'user'),
                ville=ville
            )
            
            print(f"[DEBUG] Utilisateur créé avec succès, ID: {user.id}")
            
            # Créer un token pour l'utilisateur
            token, created = Token.objects.get_or_create(user=user)
            print(f"[DEBUG] Token créé: {token.key[:10]}...")
            
            return Response({
                'message': 'Utilisateur créé avec succès',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': getattr(user, 'role', 'user'),
                    'ville': getattr(user, 'ville', '')
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"[ERREUR] Exception lors de l'inscription: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'Erreur lors de la création: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Gardons aussi la vue basée sur les fonctions en backup
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Inscription d'un nouvel utilisateur
    """
    try:
        data = request.data
        print(f"[DEBUG] Tentative d'inscription avec les données: {data}")
        
        # Vérifications des champs obligatoires
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username:
            print("[DEBUG] Nom d'utilisateur manquant")
            return Response({
                'error': 'Le nom d\'utilisateur est obligatoire'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            print("[DEBUG] Email manquant")
            return Response({
                'error': 'L\'email est obligatoire'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not password or len(password) < 6:
            print("[DEBUG] Mot de passe invalide")
            return Response({
                'error': 'Le mot de passe doit contenir au moins 6 caractères'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que l'email n'existe pas déjà
        if User.objects.filter(email=email).exists():
            print(f"[DEBUG] Email {email} existe déjà")
            return Response({
                'error': 'Un utilisateur avec cet email existe déjà'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Vérifier que le nom d'utilisateur n'existe pas déjà
        if User.objects.filter(username=username).exists():
            print(f"[DEBUG] Username {username} existe déjà")
            return Response({
                'error': 'Ce nom d\'utilisateur est déjà pris'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"[DEBUG] Création de l'utilisateur {username} avec email {email}")
        
        # Récupérer la ville depuis le frontend (priorité au champ 'ville', puis 'city')
        ville = data.get('ville', '') or data.get('city', '')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=data.get('role', 'user'),
            ville=ville
        )
        
        print(f"[DEBUG] Utilisateur créé avec succès, ID: {user.id}")
        
        # Créer un token pour l'utilisateur
        token, created = Token.objects.get_or_create(user=user)
        print(f"[DEBUG] Token créé: {token.key[:10]}...")
        
        return Response({
            'message': 'Utilisateur créé avec succès',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': getattr(user, 'role', 'user'),
                'ville': getattr(user, 'ville', '')
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"[ERREUR] Exception lors de l'inscription: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Erreur lors de la création: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    """
    Vue pour la connexion des utilisateurs
    """
    permission_classes = (AllowAny,)
    authentication_classes = ()
    
    def post(self, request):
        """
        Connexion d'un utilisateur
        """
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                return Response({
                    'error': 'Email et mot de passe requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Authentifier l'utilisateur
            user = authenticate(username=email, password=password)
            
            if user is None:
                return Response({
                    'error': 'Email ou mot de passe incorrect'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Si c'est une mairie, associer automatiquement sa ville
            if user.role == 'mairie':
                from .models import Mairie
                from .utils import normalize_name
                
                # Si l'utilisateur a déjà une ville définie, on l'utilise (nouveau système)
                if user.ville:
                    # S'assurer que la normalisation est faite
                    if not user.ville_normalized:
                        user.ville_normalized = normalize_name(user.ville)
                        user.save()
                    
                    # Créer automatiquement l'entrée Mairie si elle n'existe pas
                    mairie, created = Mairie.objects.get_or_create(
                        nom=user.ville,
                        defaults={
                            'email': email,
                            'password': user.password,  # Déjà hashé
                            'nb_poubelles': 0,
                            'seuil_alertes': 10
                        }
                    )
                    if created:
                        print(f"[DEBUG] Nouvelle mairie créée: {mairie.nom}")
                    else:
                        print(f"[DEBUG] Mairie existante trouvée: {mairie.nom}")
                        
                    print(f"[DEBUG] Mairie connectée: {user.ville} - Email: {email}")
                    print(f"[DEBUG] Ville normalisée: {user.ville_normalized}")
                else:
                    # Essayer de trouver la mairie par email (ancien système)
                    try:
                        mairie = Mairie.objects.get(email=email)
                        user.ville = mairie.nom
                        user.ville_normalized = normalize_name(mairie.nom)
                        user.save()
                        print(f"[DEBUG] Mairie trouvée par email: {mairie.nom}")
                    except Mairie.DoesNotExist:
                        print(f"[WARNING] Aucune mairie trouvée pour l'email: {email}")
                        # Optionnel: on peut toujours laisser la connexion se faire
            
            # Créer ou récupérer le token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Connexion réussie',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'ville': user.ville,
                    'points': user.points
                },
                'redirect_to': self.get_dashboard_url(user.role)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Erreur lors de la connexion: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_dashboard_url(self, role):
        """
        Retourne l'URL du dashboard selon le rôle
        """
        dashboard_urls = {
            'user': '/dashboard/user',
            'mairie': '/dashboard/mairie',
            'admin': '/dashboard/admin'
        }
        return dashboard_urls.get(role, '/dashboard/user')


# Gardons aussi la vue basée sur les fonctions en backup
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Connexion d'un utilisateur
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authentifier l'utilisateur
        user = authenticate(username=email, password=password)
        
        if user is None:
            return Response({
                'error': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Si c'est une mairie, associer automatiquement sa ville
        if user.role == 'mairie':
            from .models import Mairie
            from .utils import normalize_name
            
            # Si l'utilisateur a déjà une ville définie, on l'utilise (nouveau système)
            if user.ville:
                # S'assurer que la normalisation est faite
                if not user.ville_normalized:
                    user.ville_normalized = normalize_name(user.ville)
                    user.save()
                
                # Créer automatiquement l'entrée Mairie si elle n'existe pas
                mairie, created = Mairie.objects.get_or_create(
                    nom=user.ville,
                    defaults={
                        'email': email,
                        'password': user.password,  # Déjà hashé
                        'nb_poubelles': 0,
                        'seuil_alertes': 10
                    }
                )
                if created:
                    print(f"[DEBUG] Nouvelle mairie créée: {mairie.nom}")
                else:
                    print(f"[DEBUG] Mairie existante trouvée: {mairie.nom}")
                    
                print(f"[DEBUG] Mairie connectée: {user.ville} - Email: {email}")
                print(f"[DEBUG] Ville normalisée: {user.ville_normalized}")
            else:
                # Essayer de trouver la mairie par email (ancien système)
                try:
                    mairie = Mairie.objects.get(email=email)
                    user.ville = mairie.nom
                    user.ville_normalized = normalize_name(mairie.nom)
                    user.save()
                    print(f"[DEBUG] Mairie trouvée par email: {mairie.nom}")
                except Mairie.DoesNotExist:
                    print(f"[WARNING] Aucune mairie trouvée pour l'email: {email}")
                    # Optionnel: on peut toujours laisser la connexion se faire
        
        # Créer ou récupérer le token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Connexion réussie',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'ville': user.ville,
                'points': user.points
            },
            'redirect_to': get_dashboard_url(user.role)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la connexion: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Déconnexion d'un utilisateur
    """
    try:
        # Supprimer le token
        request.user.auth_token.delete()
        return Response({
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la déconnexion: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Récupérer le profil de l'utilisateur connecté avec rang et points
    """
    from .models import Image
    from django.db.models import Count
    
    user = request.user
    print(f"[DEBUG] Récupération profil pour: {user.username} (ID: {user.id})")
    
    # Calculer le nombre d'images uploadées par l'utilisateur
    user_images_count = Image.objects.filter(user=user).count()
    
    # Calculer le rang basé sur le nombre d'images
    from .models import User
    users_with_more_images = User.objects.annotate(
        image_count=Count('images_uploadees')
    ).filter(image_count__gt=user_images_count).count()
    rank = users_with_more_images + 1
    
    # Calculer les points (10 points par image uploadée)
    points = user_images_count * 10
    
    response_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': getattr(user, 'role', 'user'),
        'ville': getattr(user, 'ville', ''),
        'ville_normalized': getattr(user, 'ville_normalized', ''),
        'points': points,
        'rank': rank,
        'avatar': '/account/plante.png',  # Avatar par défaut
        'date_joined': user.date_joined,
        'images_uploaded': user_images_count
    }
    
    print(f"[DEBUG] Données profil renvoyées: {response_data}")
    return Response(response_data, status=status.HTTP_200_OK)


def get_dashboard_url(role):
    """
    Retourne l'URL du dashboard selon le rôle
    """
    dashboard_urls = {
        'user': '/dashboard/user',
        'mairie': '/dashboard/mairie',
        'admin': '/dashboard/admin'
    }
    return dashboard_urls.get(role, '/dashboard/user')
