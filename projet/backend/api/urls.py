from django.urls import path
from . import views
from . import admin_views
from . import auth_views, user_views, dashboard_views, image_views
from . import profile_views, classement_views, export_views
from . import competition_views
from .waste_analysis import analyze_waste_image, batch_analyze_images
from .ml_views import analyze_single_image, create_batch_analysis, get_batch_status, list_batch_analyses, export_ml_dataset
from . import geo_views
from . import dl_views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Authentification
    path('auth/register/', auth_views.RegisterView.as_view(), name='register'),
    path('auth/register-func/', auth_views.register_user, name='register-func'),  # Backup
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/login-func/', auth_views.login_user, name='login-func'),  # Backup
    path('auth/logout/', auth_views.logout_user, name='logout'),
    path('auth/profile/', auth_views.user_profile, name='user-profile'),
    
    # APIs utilisateur pour le frontend
    path('user-data/', user_views.get_user_data, name='user-data'),
    path('load-user-data/', user_views.load_user_data, name='load-user-data'),
    path('loadUserData/', user_views.load_user_data, name='load-user-data-alt'),  # Alternative pour frontend
    path('save-profile/', user_views.save_user_profile, name='save-profile'),
    path('create-mairie-account/', user_views.create_mairie_account, name='create-mairie-account'),
    
    # Dashboards par rôle
    path('dashboard/user/', dashboard_views.dashboard_user, name='dashboard-user'),
    path('dashboard/mairie/', dashboard_views.dashboard_mairie, name='dashboard-mairie'),
    path('dashboard/admin/', dashboard_views.dashboard_admin, name='dashboard-admin'),
    path('dashboard-user-data/', dashboard_views.dashboard_user_data, name='dashboard-user-data'),
    
    # Images
    path('upload/', image_views.ImageUploadView.as_view(), name='image-upload'),
    path('upload', image_views.ImageUploadView.as_view(), name='image-upload-no-slash'),
    path('batch-upload-zip/', image_views.batch_upload_zip, name='batch-upload-zip'),
    path('annotate/<int:image_id>/', image_views.annotate_image, name='annotate-image'),
    path('images/', image_views.ImageListView.as_view(), name='image-list'),
    path('images/<int:pk>/', image_views.ImageDetailView.as_view(), name='image-detail'),
    path('images/<int:pk>/annotate/', image_views.ImageAnnotationView.as_view(), name='image-annotate'),
    
    # API de test et statistiques
    path('test-user-data/', views.test_user_data, name='test-user-data'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path('export-csv/', views.export_images_csv, name='export-csv'),
path('rue-analysis/', views.rue_analysis, name='rue-analysis'),
    path('recent-uploads/', views.recent_uploads, name='recent-uploads'),
    
    # URLs pour l'administration
    path('admin/dashboard/', admin_views.dashboard_admin, name='admin-dashboard'),
    path('admin/analyse/<int:image_id>/', admin_views.analyse_details, name='admin-analyse-details'),
    path('admin/mairie-stats/', admin_views.mairie_stats_view, name='admin-mairie-stats'),
    path('admin/modifier-seuil/', admin_views.modifier_seuil_view, name='admin-modifier-seuil'),
    path('admin/tester-alerte/', admin_views.tester_alerte_view, name='admin-tester-alerte'),
    path('admin/historique-alertes/', admin_views.historique_alertes_view, name='admin-historique-alertes'),
    
    # API Analyse d'images MC_fusion
    path('analyze-waste/', analyze_waste_image, name='analyze-waste'),
    path('analyze-batch/', batch_analyze_images, name='analyze-batch'),
    
    # Nouvelles URL pour l'intégration ML
    path('ml/analyze-image/', analyze_single_image, name='ml-analyze-image'),
    path('ml/create-batch/', create_batch_analysis, name='ml-create-batch'),
    path('ml/batch-status/<int:batch_id>/', get_batch_status, name='ml-batch-status'),
    path('ml/batch-list/', list_batch_analyses, name='ml-batch-list'),
    path('ml/export-dataset/', export_ml_dataset, name='ml-export-dataset'),

    # Profil utilisateur et photo de profil
    path('profile/upload-avatar/', profile_views.upload_avatar, name='upload-avatar'),
    path('profile/delete-avatar/', profile_views.delete_avatar, name='delete-avatar'),
    path('profile/update/', profile_views.update_profile, name='update-profile'),
    
    # Système de classement
    path('classement/global/', classement_views.classement_global, name='classement-global'),
    path('classement/ville/', classement_views.classement_ville, name='classement-ville'),
    path('classement/mes-stats/', classement_views.mes_stats, name='mes-stats'),
    path('classement/mon-classement/', classement_views.mon_classement, name='mon-classement'),
    
    # APIs pour la compétition
    path('competition/users/', competition_views.competition_users, name='competition-users'),
    path('competition/mairies/', competition_views.competition_mairies, name='competition-mairies'),
    
    # Export CSV poubelles pleines
    path('export/poubelles-pleines/', export_views.export_poubelles_pleines_csv, name='export-poubelles-pleines'),
    path('export/statistiques-villes/', export_views.export_statistiques_villes_csv, name='export-stats-villes'),
    path('export/preview/', export_views.preview_export_csv, name='preview-export'),
    path('export/stats/', export_views.stats_export_disponible, name='stats-export'),
    
    # API Deep Learning (YOLO)
    path('dl/stats/', dl_views.dl_dashboard_stats, name='dl-dashboard-stats'),
    path('dl/process-image/', dl_views.DLViewSet.as_view({'post': 'process_image'}), name='dl-process-image'),
    path('dl/batch-process/', dl_views.DLViewSet.as_view({'post': 'batch_process'}), name='dl-batch-process'),
    path('dl/recent-predictions/', dl_views.DLViewSet.as_view({'get': 'recent_predictions'}), name='dl-recent-predictions'),
    path('dl/accuracy-report/', dl_views.DLViewSet.as_view({'get': 'accuracy_report'}), name='dl-accuracy-report'),
]
