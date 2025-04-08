from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    current_streak = models.IntegerField(
        default=0, help_text="Current consecutive days with activity")
    longest_streak = models.IntegerField(
        default=0, help_text="Longest streak of consecutive days with activity")
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, points=100)  # Starting points


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class ActivityType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default="fas fa-running")
    points = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ActivityLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE)
    date = models.DateField()
    duration = models.IntegerField(
        help_text="Duration in minutes", null=True, blank=True)
    distance = models.FloatField(
        help_text="Distance in kilometers", null=True, blank=True)
    calories = models.IntegerField(
        help_text="Calories burned", null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default="manual",
                              choices=(
                                  ("manual", "Manual Entry"),
                                  ("fitbit", "Fitbit"),
                                  ("googlefit", "Google Fit"),
                                  ("applehealth", "Apple Health"),
                                  ("strava", "Strava"),
                                  ("garmin", "Garmin"),
                              ))

    def __str__(self):
        return f"{self.user.username} - {self.activity_type.name} on {self.date}"

    class Meta:
        ordering = ['-date', '-created_at']


class Challenge(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    target_count = models.IntegerField(
        help_text="Target number of activities or count")
    activity_type = models.ForeignKey(
        ActivityType, on_delete=models.CASCADE, null=True, blank=True)
    points_reward = models.IntegerField(default=100)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='upcoming')
    participants = models.ManyToManyField(
        User, related_name='challenges', through='ChallengeParticipation')
    image = models.ImageField(
        upload_to='challenge_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    is_auto_generated = models.BooleanField(default=False)
    difficulty_level = models.CharField(max_length=20, choices=(
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ), default='intermediate')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_date']


class ChallengeParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    current_progress = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"


class Reward(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    points_required = models.IntegerField()
    image = models.ImageField(upload_to='reward_images', blank=True, null=True)
    available_quantity = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sponsor = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, choices=(
        ('discount', 'Discount'),
        ('product', 'Physical Product'),
        ('digital', 'Digital Good'),
        ('membership', 'Membership'),
        ('experience', 'Experience'),
    ), default='discount')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['points_required']


class RewardRedemption(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delivered', 'Delivered'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_spent = models.IntegerField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"

    class Meta:
        ordering = ['-created_at']


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    @property
    def total_points(self):
        """Calculate total points needed for all items in cart"""
        return sum(item.reward.points_required * item.quantity for item in self.items.all())

    @property
    def total_items(self):
        """Calculate total number of items in cart"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0


class CartItem(models.Model):
    cart = models.ForeignKey(
        ShoppingCart, on_delete=models.CASCADE, related_name='items')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'reward')

    def __str__(self):
        return f"{self.quantity} x {self.reward.name}"


class SubscriptionType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Monthly subscription amount in USD")
    features = models.TextField(
        help_text="List of features included in this subscription type")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['amount']


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='subscription')
    subscription_type = models.ForeignKey(
        SubscriptionType, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active')
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type.name}"

    @property
    def amount(self):
        return self.subscription_type.amount


# New models for enhanced gamification and API integration

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default="fas fa-medal")
    points_reward = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    achievement_type = models.CharField(max_length=50, choices=(
        ('activity_count', 'Activity Count'),
        ('streak', 'Activity Streak'),
        ('challenge', 'Challenge Completion'),
        ('points', 'Points Milestone'),
        ('special', 'Special Achievement'),
    ))
    required_count = models.IntegerField(
        default=1, help_text="Number required to earn this achievement")

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class FitnessDeviceConnection(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='fitness_connections')
    provider = models.CharField(max_length=50, choices=(
        ('fitbit', 'Fitbit'),
        ('googlefit', 'Google Fit'),
        ('applehealth', 'Apple Health'),
        ('strava', 'Strava'),
        ('garmin', 'Garmin'),
    ))
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'provider')

    def __str__(self):
        return f"{self.user.username} - {self.provider}"


class HealthMetric(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='health_metrics')
    date = models.DateField()
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    heart_rate = models.IntegerField(
        null=True, blank=True, help_text="Resting heart rate in bpm")
    sleep_duration = models.FloatField(
        null=True, blank=True, help_text="Sleep duration in hours")
    steps = models.IntegerField(null=True, blank=True, help_text="Step count")
    calories_burned = models.IntegerField(
        null=True, blank=True, help_text="Total calories burned")
    source = models.CharField(max_length=50, default="manual", choices=(
        ('manual', 'Manual Entry'),
        ('fitbit', 'Fitbit'),
        ('googlefit', 'Google Fit'),
        ('applehealth', 'Apple Health'),
        ('strava', 'Strava'),
        ('garmin', 'Garmin'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - Metrics for {self.date}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(
        upload_to='category_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(
        upload_to='product_images', blank=True, null=True)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total(self):
        return self.quantity * self.price
