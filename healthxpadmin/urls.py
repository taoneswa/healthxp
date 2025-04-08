from django.urls import path
from . import views

app_name = 'healthxpadmin'

urlpatterns = [
    # Dashboard Home
    path('', views.dashboard_home, name='dashboard_home'),

    # User Management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/update/',
         views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/',
         views.UserDeleteView.as_view(), name='user_delete'),

    # Activity Management
    path('activity-types/', views.ActivityTypeListView.as_view(),
         name='activity_type_list'),
    path('activity-types/create/', views.ActivityTypeCreateView.as_view(),
         name='activity_type_create'),
    path('activity-types/<int:pk>/update/',
         views.ActivityTypeUpdateView.as_view(), name='activity_type_update'),
    path('activity-types/<int:pk>/delete/',
         views.ActivityTypeDeleteView.as_view(), name='activity_type_delete'),

    # Activity Logs
    path('activity-logs/', views.ActivityLogListView.as_view(),
         name='activity_log_list'),
    path('activity-logs/<int:pk>/', views.ActivityLogDetailView.as_view(),
         name='activity_log_detail'),

    # Challenge Management
    path('challenges/', views.ChallengeListView.as_view(), name='challenge_list'),
    path('challenges/create/', views.ChallengeCreateView.as_view(),
         name='challenge_create'),
    path('challenges/<int:pk>/update/',
         views.ChallengeUpdateView.as_view(), name='challenge_update'),
    path('challenges/<int:pk>/delete/',
         views.ChallengeDeleteView.as_view(), name='challenge_delete'),

    # Reward Management
    path('rewards/', views.RewardListView.as_view(), name='reward_list'),
    path('rewards/create/', views.RewardCreateView.as_view(), name='reward_create'),
    path('rewards/<int:pk>/update/',
         views.RewardUpdateView.as_view(), name='reward_update'),
    path('rewards/<int:pk>/delete/',
         views.RewardDeleteView.as_view(), name='reward_delete'),

    # Subscription Type Management
    path('subscription-types/', views.SubscriptionTypeListView.as_view(),
         name='subscription_type_list'),
    path('subscription-types/create/', views.SubscriptionTypeCreateView.as_view(),
         name='subscription_type_create'),
    path('subscription-types/<int:pk>/update/',
         views.SubscriptionTypeUpdateView.as_view(), name='subscription_type_update'),
    path('subscription-types/<int:pk>/delete/',
         views.SubscriptionTypeDeleteView.as_view(), name='subscription_type_delete'),

    # Subscription Management
    path('subscriptions/', views.SubscriptionListView.as_view(),
         name='subscription_list'),
    path('subscriptions/create/', views.SubscriptionCreateView.as_view(),
         name='subscription_create'),
    path('subscriptions/<int:pk>/',
         views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('subscriptions/<int:pk>/update/',
         views.SubscriptionUpdateView.as_view(), name='subscription_update'),
    path('subscriptions/<int:pk>/cancel/',
         views.SubscriptionCancelView.as_view(), name='subscription_cancel'),
]
