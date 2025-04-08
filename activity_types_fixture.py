from healthxpfront.models import ActivityType

# Create activity types
activity_types = [
    {
        'name': 'Walking',
        'description': 'A low-impact exercise that can help maintain a healthy weight and improve mood.',
        'icon_class': 'fas fa-walking',
        'points': 10
    },
    {
        'name': 'Running',
        'description': 'A high-impact cardiovascular exercise that helps burn calories and improve heart health.',
        'icon_class': 'fas fa-running',
        'points': 15
    },
    {
        'name': 'Cycling',
        'description': 'A low-impact exercise that improves cardiovascular health and builds leg strength.',
        'icon_class': 'fas fa-biking',
        'points': 12
    },
    {
        'name': 'Swimming',
        'description': 'A full-body workout that is gentle on the joints and great for cardiovascular health.',
        'icon_class': 'fas fa-swimmer',
        'points': 15
    },
    {
        'name': 'Yoga',
        'description': 'Improves flexibility, strength, and mental well-being through poses and breathing techniques.',
        'icon_class': 'fas fa-pray',
        'points': 12
    },
    {
        'name': 'Weight Training',
        'description': 'Builds muscle strength and endurance through resistance exercises.',
        'icon_class': 'fas fa-dumbbell',
        'points': 15
    },
    {
        'name': 'Hiking',
        'description': 'An outdoor activity that combines walking with nature, providing both physical and mental benefits.',
        'icon_class': 'fas fa-mountain',
        'points': 15
    },
    {
        'name': 'Dancing',
        'description': 'A fun way to improve cardiovascular health, coordination, and mood.',
        'icon_class': 'fas fa-music',
        'points': 12
    },
    {
        'name': 'Pilates',
        'description': 'A low-impact exercise that focuses on core strength, posture, and flexibility.',
        'icon_class': 'fas fa-spa',
        'points': 12
    },
    {
        'name': 'Meditation',
        'description': 'A mental exercise that focuses on mindfulness and relaxation to reduce stress.',
        'icon_class': 'fas fa-brain',
        'points': 8
    }
]

# Save activity types to database
for activity_type in activity_types:
    ActivityType.objects.get_or_create(
        name=activity_type['name'],
        defaults={
            'description': activity_type['description'],
            'icon_class': activity_type['icon_class'],
            'points': activity_type['points']
        }
    )

print(f'{ActivityType.objects.count()} activity types created successfully!')
