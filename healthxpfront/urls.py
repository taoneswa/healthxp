from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .auth_views import CustomLoginView

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('health-galaxy-park/', views.health_galaxy_park,
         name='health_galaxy_park'),
    path('ptn/', views.ptn, name='ptn'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('events/', views.events, name='events'),
    path('research/', views.research, name='research'),
    path('appointment/', views.appointment, name='appointment'),
    path('contact/', views.contact, name='contact'),

    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(template_name='healthxpfront/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='healthxpfront/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Activity Tracking URLs
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/new/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/update/',
         views.activity_update, name='activity_update'),
    path('activities/<int:pk>/delete/',
         views.activity_delete, name='activity_delete'),

    # Challenge URLs
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/<int:pk>/', views.challenge_detail, name='challenge_detail'),
    path('my-challenges/', views.my_challenges, name='my_challenges'),

    # Reward URLs
    path('rewards/', views.reward_list, name='reward_list'),
    path('rewards/<int:pk>/', views.reward_detail, name='reward_detail'),
    path('redemption-history/', views.redemption_history,
         name='redemption_history'),

    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/update/<int:item_id>/',
         views.update_cart_item, name='update_cart_item'),
    path('cart/checkout/', views.checkout, name='checkout'),

    # Leaderboard URL
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # Achievement URLs
    path('achievements/', views.achievements, name='achievements'),

    # Health Metrics URLs
    path('health-metrics/', views.health_metrics, name='health_metrics'),

    # Fitness Device Integration URLs
    path('connect-device/<str:provider>/',
         views.connect_fitness_device, name='connect_device'),
    path('disconnect-device/<str:provider>/',
         views.disconnect_fitness_device, name='disconnect_device'),
    path('sync-fitness-data/', views.sync_fitness_data, name='sync_fitness_data'),

    # Password reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='healthxpfront/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='healthxpfront/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='healthxpfront/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='healthxpfront/password_reset_complete.html'),
         name='password_reset_complete'),

    path('my-subscription/', views.my_subscription, name='my_subscription'),
]
