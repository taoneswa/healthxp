import datetime
import requests
from django.utils import timezone
from .models import Profile, ActivityLog, HealthMetric, UserAchievement, Achievement
import logging

logger = logging.getLogger(__name__)


def update_user_streak(user):
    """
    Update user streak based on activity logs
    Returns True if streak was updated, False otherwise
    """
    profile = user.profile
    today = timezone.now().date()

    # If this is the first activity ever
    if not profile.last_activity_date:
        profile.current_streak = 1
        profile.longest_streak = 1
        profile.last_activity_date = today
        profile.save()
        return True

    # If activity was already logged today, no change in streak
    if profile.last_activity_date == today:
        return False

    # If the last activity was yesterday, increment streak
    if profile.last_activity_date == today - datetime.timedelta(days=1):
        profile.current_streak += 1
        profile.last_activity_date = today

        # Update longest streak if current exceeds it
        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak

        profile.save()

        # Check for streak achievement milestones
        check_streak_achievements(user, profile.current_streak)
        return True

    # If there's a gap in activity, reset streak
    if profile.last_activity_date < today - datetime.timedelta(days=1):
        profile.current_streak = 1
        profile.last_activity_date = today
        profile.save()
        return True

    return False


def check_streak_achievements(user, streak_count):
    """
    Check and award streak-based achievements
    """
    streak_achievements = Achievement.objects.filter(
        achievement_type='streak',
        required_count__lte=streak_count,
        is_active=True
    )

    for achievement in streak_achievements:
        # Check if user already has this achievement
        if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            # Award the achievement
            UserAchievement.objects.create(user=user, achievement=achievement)

            # Award points
            user.profile.points += achievement.points_reward
            user.profile.save()

            logger.info(
                f"User {user.username} earned streak achievement: {achievement.name}")


def check_points_achievements(user):
    """
    Check and award points milestone achievements
    """
    points = user.profile.points
    points_achievements = Achievement.objects.filter(
        achievement_type='points',
        required_count__lte=points,
        is_active=True
    )

    for achievement in points_achievements:
        # Check if user already has this achievement
        if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            # Award the achievement
            UserAchievement.objects.create(user=user, achievement=achievement)

            # Award bonus points (no recursive loop since the check is on existing points)
            user.profile.points += achievement.points_reward
            user.profile.save()

            logger.info(
                f"User {user.username} earned points achievement: {achievement.name}")


def check_activity_count_achievements(user):
    """
    Check and award activity count achievements
    """
    activity_count = ActivityLog.objects.filter(user=user).count()

    activity_achievements = Achievement.objects.filter(
        achievement_type='activity_count',
        required_count__lte=activity_count,
        is_active=True
    )

    for achievement in activity_achievements:
        # Check if user already has this achievement
        if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            # Award the achievement
            UserAchievement.objects.create(user=user, achievement=achievement)

            # Award points
            user.profile.points += achievement.points_reward
            user.profile.save()

            logger.info(
                f"User {user.username} earned activity count achievement: {achievement.name}")


# Fitness API Integration Functions

def sync_fitbit_data(user_connection):
    """
    Sync data from Fitbit API
    """
    try:
        # Get access token
        token = user_connection.access_token
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
        }

        user = user_connection.user
        today = timezone.now().date().strftime('%Y-%m-%d')

        # Get activity data
        activity_url = f'https://api.fitbit.com/1/user/-/activities/date/{today}.json'
        response = requests.get(activity_url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Log step activity if it exists and steps > 5000
            if 'summary' in data and 'steps' in data['summary'] and data['summary']['steps'] > 5000:
                steps = data['summary']['steps']
                calories = data['summary']['caloriesOut'] if 'caloriesOut' in data['summary'] else None

                # Check if we already have a step activity for today
                existing_activity = ActivityLog.objects.filter(
                    user=user,
                    date=timezone.now().date(),
                    activity_type__name__icontains='walk',
                    source='fitbit'
                ).first()

                if not existing_activity:
                    # Get walking activity type
                    from .models import ActivityType
                    walking_activity = ActivityType.objects.filter(
                        name__icontains='walk').first()

                    if walking_activity:
                        # Create activity log
                        duration = steps // 100  # Rough estimate: 100 steps per minute
                        distance = steps / 1500  # Rough estimate: 1500 steps per km

                        activity = ActivityLog(
                            user=user,
                            activity_type=walking_activity,
                            date=timezone.now().date(),
                            duration=duration,
                            distance=distance,
                            calories=calories,
                            source='fitbit',
                            notes=f'Auto-tracked from Fitbit: {steps} steps'
                        )

                        # Calculate points: base + bonus
                        activity.points_earned = walking_activity.points
                        if duration >= 60:  # If duration >= 60 minutes
                            activity.points_earned += 5
                        if distance >= 5:  # If distance >= 5 km
                            activity.points_earned += 5

                        activity.save()

                        # Update user points
                        user.profile.points += activity.points_earned
                        user.profile.save()

                        # Update streak
                        update_user_streak(user)

                        logger.info(
                            f"Synced Fitbit walking activity for {user.username}")

            # Store health metrics
            try:
                # Get sleep data
                sleep_url = f'https://api.fitbit.com/1.2/user/-/sleep/date/{today}.json'
                sleep_response = requests.get(sleep_url, headers=headers)

                sleep_duration = None
                if sleep_response.status_code == 200:
                    sleep_data = sleep_response.json()
                    if 'summary' in sleep_data and 'totalMinutesAsleep' in sleep_data['summary']:
                        sleep_minutes = sleep_data['summary']['totalMinutesAsleep']
                        sleep_duration = sleep_minutes / 60  # Convert to hours

                # Create health metric record
                HealthMetric.objects.update_or_create(
                    user=user,
                    date=timezone.now().date(),
                    defaults={
                        'steps': data['summary']['steps'] if 'summary' in data and 'steps' in data['summary'] else None,
                        'calories_burned': data['summary']['caloriesOut'] if 'summary' in data and 'caloriesOut' in data['summary'] else None,
                        'sleep_duration': sleep_duration,
                        'source': 'fitbit'
                    }
                )

                logger.info(
                    f"Synced Fitbit health metrics for {user.username}")

            except Exception as e:
                logger.error(f"Error syncing Fitbit health metrics: {str(e)}")

            # Update last sync time
            user_connection.last_sync = timezone.now()
            user_connection.save()

            return True

        elif response.status_code == 401:
            # Token expired, needs refresh
            user_connection.is_active = False
            user_connection.save()
            logger.warning(f"Fitbit token expired for {user.username}")
            return False

        else:
            logger.error(
                f"Fitbit API error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error syncing Fitbit data: {str(e)}")
        return False


def sync_google_fit_data(user_connection):
    """
    Sync data from Google Fit API (simplified implementation)
    """
    # Implementation would be similar to Fitbit but using Google Fit API
    # This is a placeholder for the actual implementation
    logger.info(
        f"Google Fit sync for {user_connection.user.username} (placeholder)")
    return True


def generate_auto_challenges():
    """
    Generate automatic challenges based on system data
    """
    from .models import Challenge, ActivityType
    from django.db.models import Avg, Count
    import random

    today = timezone.now().date()
    end_date = today + datetime.timedelta(days=30)  # One month challenge

    # Get popular activity types
    popular_activities = ActivityType.objects.annotate(
        log_count=Count('activitylog')
    ).filter(
        log_count__gt=0,
        is_active=True
    ).order_by('-log_count')[:5]

    if not popular_activities:
        logger.warning(
            "No popular activities found for auto-challenge generation")
        return

    # Check if we already have auto-generated challenges active
    existing_auto_challenges = Challenge.objects.filter(
        is_auto_generated=True,
        status='active'
    ).count()

    if existing_auto_challenges >= 3:
        logger.info("Already have 3 or more auto-generated challenges active")
        return

    # Get average counts for activity types to set reasonable targets
    for activity_type in popular_activities:
        avg_count = ActivityLog.objects.filter(
            activity_type=activity_type
        ).values('user').annotate(
            user_count=Count('id')
        ).aggregate(Avg('user_count'))['user_count__avg'] or 5

        # Set target slightly higher than average
        target_count = int(avg_count * 1.2) + 1

        # Randomize names and descriptions
        challenge_templates = [
            {
                'title': f"{activity_type.name} Challenge",
                'description': f"Complete {target_count} {activity_type.name} activities in the next month."
            },
            {
                'title': f"{activity_type.name} Champion",
                'description': f"Show your dedication by completing {target_count} {activity_type.name} activities."
            },
            {
                'title': f"Master of {activity_type.name}",
                'description': f"Become a master by logging {target_count} {activity_type.name} activities."
            }
        ]

        template = random.choice(challenge_templates)

        # Create the challenge
        Challenge.objects.create(
            title=template['title'],
            description=template['description'],
            start_date=today,
            end_date=end_date,
            target_count=target_count,
            activity_type=activity_type,
            points_reward=target_count * 10,  # Scale reward with difficulty
            status='active',
            is_auto_generated=True,
            difficulty_level='intermediate'
        )

        logger.info(f"Created auto-generated challenge: {template['title']}")

        # Limit to creating just one new challenge at a time
        break
