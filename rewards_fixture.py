from healthxpfront.models import Reward

# Create rewards
rewards = [
    {
        'name': 'HealthXP Water Bottle',
        'description': 'Stay hydrated in style with our branded eco-friendly water bottle.',
        'points_required': 500,
        'available_quantity': 20
    },
    {
        'name': 'Fitness Tracker',
        'description': 'Track your activities, sleep, and heart rate with this smart fitness band.',
        'points_required': 2000,
        'available_quantity': 5
    },
    {
        'name': '30-Day Premium Subscription',
        'description': 'Upgrade to our Premium tier for 30 days and unlock all features.',
        'points_required': 800,
        'available_quantity': 100
    },
    {
        'name': 'Yoga Mat',
        'description': 'A high-quality non-slip yoga mat for your home workouts.',
        'points_required': 1000,
        'available_quantity': 10
    },
    {
        'name': 'Healthy Recipe Cookbook',
        'description': 'Digital cookbook featuring 100+ nutritious and delicious recipes.',
        'points_required': 500,
        'available_quantity': 50
    },
    {
        'name': 'Personal Training Session',
        'description': 'One-hour virtual personal training session with a certified trainer.',
        'points_required': 1500,
        'available_quantity': 8
    },
    {
        'name': 'HealthXP T-Shirt',
        'description': 'Comfortable and stylish workout t-shirt with our logo.',
        'points_required': 700,
        'available_quantity': 15
    },
    {
        'name': 'Meditation App Subscription',
        'description': '3-month subscription to a premium meditation app.',
        'points_required': 900,
        'available_quantity': 10
    },
    {
        'name': 'Gift Card - Sports Store',
        'description': '$25 gift card for a popular sports equipment retailer.',
        'points_required': 1200,
        'available_quantity': 5
    },
    {
        'name': 'Nutrition Consultation',
        'description': 'Virtual consultation with a registered dietitian.',
        'points_required': 1800,
        'available_quantity': 3
    }
]

# Save rewards to database
for reward in rewards:
    Reward.objects.get_or_create(
        name=reward['name'],
        defaults={
            'description': reward['description'],
            'points_required': reward['points_required'],
            'available_quantity': reward['available_quantity'],
            'is_active': True
        }
    )

print(f'{Reward.objects.count()} rewards created successfully!')
