from django.contrib import admin
from .models import (
    Profile, ActivityType, ActivityLog, Challenge, ChallengeParticipation,
    Reward, RewardRedemption, Subscription, Achievement, UserAchievement,
    FitnessDeviceConnection, HealthMetric, Contact, SubscriptionType
)

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'date_joined',
                    'current_streak', 'longest_streak')
    search_fields = ('user__username', 'user__email')


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'points', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'date',
                    'duration', 'points_earned', 'source')
    list_filter = ('activity_type', 'date', 'source')
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'date'


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'activity_type', 'start_date',
                    'end_date', 'status', 'points_reward', 'is_featured', 'is_auto_generated')
    list_filter = ('status', 'activity_type', 'is_featured',
                   'is_auto_generated', 'difficulty_level')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'


@admin.register(ChallengeParticipation)
class ChallengeParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'current_progress', 'completed')
    list_filter = ('completed', 'challenge')
    search_fields = ('user__username',)


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required',
                    'available_quantity', 'is_active', 'category', 'sponsor')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description', 'sponsor')


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'points_spent', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'reward__name')
    date_hierarchy = 'created_at'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'start_date',
                    'end_date', 'status', 'auto_renew')
    list_filter = ('subscription_type', 'status', 'auto_renew')
    search_fields = ('user__username',)
    date_hierarchy = 'start_date'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'achievement_type', 'points_reward',
                    'required_count', 'is_active')
    list_filter = ('achievement_type', 'is_active')
    search_fields = ('name', 'description')


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'date_earned')
    list_filter = ('achievement', 'date_earned')
    search_fields = ('user__username', 'achievement__name')
    date_hierarchy = 'date_earned'


@admin.register(FitnessDeviceConnection)
class FitnessDeviceConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'is_active', 'last_sync')
    list_filter = ('provider', 'is_active')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'weight', 'steps',
                    'heart_rate', 'sleep_duration', 'source')
    list_filter = ('date', 'source')
    search_fields = ('user__username',)
    date_hierarchy = 'date'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'amount', 'is_active', 'subscriber_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')
    ordering = ('amount',)
    readonly_fields = ('created_at', 'updated_at')

    def subscriber_count(self, obj):
        return obj.subscriptions.filter(status='active').count()
    subscriber_count.short_description = 'Active Subscribers'
