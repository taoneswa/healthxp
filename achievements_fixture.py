import os
import django
import sys


def main():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthxp.settings')
    django.setup()

    # Import models after Django is set up
    from healthxpfront.models import Achievement

    # Delete existing achievements to avoid duplicates
    Achievement.objects.all().delete()

    # Define achievements to create
    achievements = [
        # Activity Count Achievements
        {
            'name': 'First Steps',
            'description': 'Log your first activity',
            'icon_class': 'fas fa-shoe-prints',
            'points_reward': 20,
            'achievement_type': 'activity_count',
            'required_count': 1,
        },
        {
            'name': 'Getting Active',
            'description': 'Complete 5 activities',
            'icon_class': 'fas fa-running',
            'points_reward': 50,
            'achievement_type': 'activity_count',
            'required_count': 5,
        },
        {
            'name': 'Fitness Enthusiast',
            'description': 'Complete 20 activities',
            'icon_class': 'fas fa-dumbbell',
            'points_reward': 100,
            'achievement_type': 'activity_count',
            'required_count': 20,
        },
        {
            'name': 'Health Champion',
            'description': 'Complete 50 activities',
            'icon_class': 'fas fa-award',
            'points_reward': 200,
            'achievement_type': 'activity_count',
            'required_count': 50,
        },
        {
            'name': 'Fitness Guru',
            'description': 'Complete 100 activities',
            'icon_class': 'fas fa-crown',
            'points_reward': 500,
            'achievement_type': 'activity_count',
            'required_count': 100,
        },

        # Streak Achievements
        {
            'name': 'Consistent',
            'description': 'Maintain a 3-day activity streak',
            'icon_class': 'fas fa-fire',
            'points_reward': 30,
            'achievement_type': 'streak',
            'required_count': 3,
        },
        {
            'name': 'Dedicated',
            'description': 'Maintain a 7-day activity streak',
            'icon_class': 'fas fa-fire-alt',
            'points_reward': 75,
            'achievement_type': 'streak',
            'required_count': 7,
        },
        {
            'name': 'Unstoppable',
            'description': 'Maintain a 14-day activity streak',
            'icon_class': 'fas fa-bolt',
            'points_reward': 150,
            'achievement_type': 'streak',
            'required_count': 14,
        },
        {
            'name': 'Iron Will',
            'description': 'Maintain a 30-day activity streak',
            'icon_class': 'fas fa-medal',
            'points_reward': 300,
            'achievement_type': 'streak',
            'required_count': 30,
        },

        # Points Achievements
        {
            'name': 'Point Collector',
            'description': 'Earn 250 total points',
            'icon_class': 'fas fa-coins',
            'points_reward': 25,
            'achievement_type': 'points',
            'required_count': 250,
        },
        {
            'name': 'Point Hunter',
            'description': 'Earn 500 total points',
            'icon_class': 'fas fa-gem',
            'points_reward': 50,
            'achievement_type': 'points',
            'required_count': 500,
        },
        {
            'name': 'Point Master',
            'description': 'Earn 1,000 total points',
            'icon_class': 'fas fa-trophy',
            'points_reward': 100,
            'achievement_type': 'points',
            'required_count': 1000,
        },
        {
            'name': 'Point Champion',
            'description': 'Earn 2,500 total points',
            'icon_class': 'fas fa-star',
            'points_reward': 250,
            'achievement_type': 'points',
            'required_count': 2500,
        },
        {
            'name': 'Point Legend',
            'description': 'Earn 5,000 total points',
            'icon_class': 'fas fa-crown',
            'points_reward': 500,
            'achievement_type': 'points',
            'required_count': 5000,
        },

        # Challenge Achievements
        {
            'name': 'Challenge Accepted',
            'description': 'Complete your first challenge',
            'icon_class': 'fas fa-flag-checkered',
            'points_reward': 50,
            'achievement_type': 'challenge',
            'required_count': 1,
        },
        {
            'name': 'Challenge Crusher',
            'description': 'Complete 5 challenges',
            'icon_class': 'fas fa-tasks',
            'points_reward': 100,
            'achievement_type': 'challenge',
            'required_count': 5,
        },
        {
            'name': 'Challenge Master',
            'description': 'Complete 10 challenges',
            'icon_class': 'fas fa-trophy',
            'points_reward': 200,
            'achievement_type': 'challenge',
            'required_count': 10,
        },

        # Special Achievements
        {
            'name': 'Early Bird',
            'description': 'Log an activity before 7 AM',
            'icon_class': 'fas fa-sun',
            'points_reward': 30,
            'achievement_type': 'special',
            'required_count': 1,
        },
        {
            'name': 'Night Owl',
            'description': 'Log an activity after 10 PM',
            'icon_class': 'fas fa-moon',
            'points_reward': 30,
            'achievement_type': 'special',
            'required_count': 1,
        },
        {
            'name': 'Social Butterfly',
            'description': 'Share an activity on social media',
            'icon_class': 'fas fa-share-alt',
            'points_reward': 25,
            'achievement_type': 'special',
            'required_count': 1,
        },
    ]

    # Create the achievements
    for achievement_data in achievements:
        Achievement.objects.create(**achievement_data)

    print(f"Created {len(achievements)} achievements")


if __name__ == "__main__":
    main()
