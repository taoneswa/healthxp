from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import Coalesce
from django.db import models
from django.utils import timezone
from django.http import JsonResponse
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    ActivityLogForm, ChallengeParticipationForm, RewardRedemptionForm, SubscriptionForm,
    ContactForm
)
from .models import (
    Profile, ActivityType, ActivityLog, Challenge, ChallengeParticipation,
    Reward, RewardRedemption, Subscription, Achievement, UserAchievement,
    FitnessDeviceConnection, HealthMetric, ShoppingCart, CartItem, SubscriptionType
)
from .utils import (
    update_user_streak, check_points_achievements,
    check_activity_count_achievements, sync_fitbit_data
)
import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.


def home(request):
    return render(request, 'healthxpfront/home.html')


def about(request):
    return render(request, 'healthxpfront/about.html')


def health_galaxy_park(request):
    return render(request, 'healthxpfront/health_galaxy_park.html')


def ptn(request):
    return render(request, 'healthxpfront/ptn.html')


def subscriptions(request):
    # Get subscription types from database
    subscription_plans = SubscriptionType.objects.filter(
        is_active=True,
        code__in=['silver', 'gold', 'platinum']
    ).order_by('amount')

    # Get cooperative subscription types
    coop_plans = SubscriptionType.objects.filter(
        is_active=True,
        code__startswith='coop_'
    ).order_by('amount')

    # Format plans for template
    formatted_plans = []
    for plan in subscription_plans:
        formatted_plans.append({
            'name': plan.name,
            'price': float(plan.amount),
            'points': int(float(plan.amount) * 100),  # Points based on amount
            'description': plan.description,
            'features': [feature.strip() for feature in plan.features.split('\n') if feature.strip()],
            'type': plan.code,
            'image': f'healthxpfront/images/medals/{plan.code}-medal.png'
        })

    formatted_coop_plans = []
    for plan in coop_plans:
        formatted_coop_plans.append({
            'name': plan.name,
            'price': float(plan.amount),
            'points': int(float(plan.amount) * 100),  # Points based on amount
            'description': plan.description,
            'features': [feature.strip() for feature in plan.features.split('\n') if feature.strip()],
            'type': plan.code,
            'image': f'healthxpfront/images/medals/{plan.code.replace("coop_", "")}-medal.png'
        })

    context = {
        'subscription_plans': formatted_plans,
        'coop_plans': formatted_coop_plans
    }

    # If user is logged in, check if they have an active subscription
    if request.user.is_authenticated:
        try:
            subscription = Subscription.objects.get(user=request.user)
            context['current_subscription'] = subscription
        except Subscription.DoesNotExist:
            pass

        if request.method == 'POST':
            subscription_type_code = request.POST.get('subscription_type')
            auto_renew = request.POST.get('auto_renew', 'False') == 'True'

            try:
                subscription_type = SubscriptionType.objects.get(
                    code=subscription_type_code, is_active=True)
                points_to_award = int(float(subscription_type.amount) * 100)

                # Create or update subscription
                try:
                    subscription = Subscription.objects.get(user=request.user)

                    # Only award points if changing to a different plan
                    if subscription.subscription_type != subscription_type:
                        # Award points to user profile
                        if points_to_award > 0:
                            profile = request.user.profile
                            profile.points += points_to_award
                            profile.save()
                            messages.success(
                                request, f'You\'ve been awarded {points_to_award} points for your subscription!')

                    subscription.subscription_type = subscription_type
                    subscription.auto_renew = auto_renew
                    subscription.status = 'active'

                    # Set end date based on subscription type (1 year for all plans)
                    subscription.end_date = timezone.now() + datetime.timedelta(days=365)
                    subscription.save()

                except Subscription.DoesNotExist:
                    # Create new subscription
                    end_date = timezone.now() + datetime.timedelta(days=365)

                    Subscription.objects.create(
                        user=request.user,
                        subscription_type=subscription_type,
                        auto_renew=auto_renew,
                        status='active',
                        end_date=end_date
                    )

                    # Award points to new subscribers
                    if points_to_award > 0:
                        profile = request.user.profile
                        profile.points += points_to_award
                        profile.save()
                        messages.success(
                            request, f'You\'ve been awarded {points_to_award} points for your subscription!')

                messages.success(
                    request, f'Your subscription has been updated to {subscription_type.name}!')
                return redirect('subscriptions')

            except SubscriptionType.DoesNotExist:
                messages.error(request, 'Invalid subscription type selected.')
                return redirect('subscriptions')

    return render(request, 'healthxpfront/subscriptions.html', context)


def events(request):
    return render(request, 'healthxpfront/events.html')


def research(request):
    return render(request, 'healthxpfront/research.html')


def appointment(request):
    return render(request, 'healthxpfront/appointment.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Thank you for your message. We will get back to you soon!')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'healthxpfront/contact.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'healthxpfront/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # Get user achievements
    achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement').order_by('-date_earned')

    # Get user health metrics history
    health_metrics = HealthMetric.objects.filter(
        user=request.user
    ).order_by('-date')[:10]

    # Get connected fitness devices
    fitness_connections = FitnessDeviceConnection.objects.filter(
        user=request.user,
        is_active=True
    )

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'achievements': achievements,
        'health_metrics': health_metrics,
        'fitness_connections': fitness_connections
    }
    return render(request, 'healthxpfront/profile.html', context)


@login_required
def dashboard(request):
    # Get latest activities
    recent_activities = ActivityLog.objects.filter(
        user=request.user).order_by('-date', '-created_at')[:5]

    # Get active challenges
    active_challenges = Challenge.objects.filter(
        status='active').order_by('-start_date')[:3]

    # Get user's challenge participation
    user_participations = ChallengeParticipation.objects.filter(
        user=request.user,
        challenge__status='active'
    ).select_related('challenge')[:3]

    # Get available rewards
    available_rewards = Reward.objects.filter(
        is_active=True,
        available_quantity__gt=0,
        points_required__lte=request.user.profile.points
    ).order_by('points_required')[:3]

    # Get user's stats
    weekly_activities_count = ActivityLog.objects.filter(
        user=request.user,
        date__gte=timezone.now().date() - datetime.timedelta(days=7)
    ).count()

    total_rewards_redeemed = RewardRedemption.objects.filter(
        user=request.user
    ).count()

    # Get recent achievements
    recent_achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement').order_by('-date_earned')[:3]

    # Get latest health metrics
    latest_metrics = HealthMetric.objects.filter(
        user=request.user
    ).order_by('-date').first()

    # Get fitness device connections
    fitness_connections = FitnessDeviceConnection.objects.filter(
        user=request.user,
        is_active=True
    )

    # Get streak data
    current_streak = request.user.profile.current_streak
    longest_streak = request.user.profile.longest_streak

    context = {
        'recent_activities': recent_activities,
        'active_challenges': active_challenges,
        'user_participations': user_participations,
        'available_rewards': available_rewards,
        'weekly_activities_count': weekly_activities_count,
        'total_rewards_redeemed': total_rewards_redeemed,
        'recent_achievements': recent_achievements,
        'latest_metrics': latest_metrics,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'fitness_connections': fitness_connections
    }

    return render(request, 'healthxpfront/dashboard.html', context)


@login_required
def activity_list(request):
    activities = ActivityLog.objects.filter(
        user=request.user).order_by('-date', '-created_at')

    # Filter by date if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    activity_type = request.GET.get('activity_type')

    if start_date:
        try:
            start_date = datetime.datetime.strptime(
                start_date, '%Y-%m-%d').date()
            activities = activities.filter(date__gte=start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            activities = activities.filter(date__lte=end_date)
        except ValueError:
            pass

    if activity_type:
        activities = activities.filter(activity_type__id=activity_type)

    # Get activity types for the filter dropdown
    activity_types = ActivityType.objects.filter(is_active=True)

    # Calculate totals
    total_points = activities.aggregate(total_points=Sum('points_earned'))[
        'total_points'] or 0
    total_duration = activities.aggregate(total_duration=Sum('duration'))[
        'total_duration'] or 0
    total_distance = activities.aggregate(total_distance=Sum('distance'))[
        'total_distance'] or 0
    total_calories = activities.aggregate(total_calories=Sum('calories'))[
        'total_calories'] or 0

    context = {
        'activities': activities,
        'activity_types': activity_types,
        'total_points': total_points,
        'total_duration': total_duration,
        'total_distance': total_distance,
        'total_calories': total_calories,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'activity_type': activity_type
        }
    }

    return render(request, 'healthxpfront/activity_list.html', context)


@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False, user=request.user)
            activity.save()

            # Update user profile points
            request.user.profile.points += activity.points_earned
            request.user.profile.save()

            # Update challenge progress if relevant
            update_challenge_progress(request.user, activity.activity_type, 1)

            # Update streak
            streak_updated = update_user_streak(request.user)
            if streak_updated:
                messages.info(
                    request, f'Your activity streak is now {request.user.profile.current_streak} days!')

            # Check for achievements
            check_activity_count_achievements(request.user)
            check_points_achievements(request.user)

            messages.success(
                request, f'Activity logged successfully! You earned {activity.points_earned} points.')
            return redirect('activity_list')
    else:
        form = ActivityLogForm()

    context = {
        'form': form,
        'title': 'Log Activity'
    }

    return render(request, 'healthxpfront/activity_form.html', context)


@login_required
def activity_update(request, pk):
    activity = get_object_or_404(ActivityLog, pk=pk, user=request.user)
    old_points = activity.points_earned

    if request.method == 'POST':
        form = ActivityLogForm(request.POST, instance=activity)
        if form.is_valid():
            # Save without committing to calculate points
            updated_activity = form.save(commit=False, user=request.user)

            # Update user's points - subtract old points and add new points
            point_difference = updated_activity.points_earned - old_points
            request.user.profile.points += point_difference
            request.user.profile.save()

            updated_activity.save()

            messages.success(request, f'Activity updated successfully!')
            return redirect('activity_list')
    else:
        form = ActivityLogForm(instance=activity)

    context = {
        'form': form,
        'title': 'Update Activity'
    }

    return render(request, 'healthxpfront/activity_form.html', context)


@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(ActivityLog, pk=pk, user=request.user)

    if request.method == 'POST':
        # Reduce user's points
        request.user.profile.points -= activity.points_earned
        request.user.profile.save()

        # Update challenge progress if relevant (decrement)
        update_challenge_progress(request.user, activity.activity_type, -1)

        activity.delete()
        messages.success(request, f'Activity deleted successfully!')
        return redirect('activity_list')

    context = {
        'activity': activity
    }

    return render(request, 'healthxpfront/activity_confirm_delete.html', context)


@login_required
def challenge_list(request):
    # Get challenges based on status
    active_challenges = Challenge.objects.filter(
        status='active').order_by('-start_date')
    upcoming_challenges = Challenge.objects.filter(
        status='upcoming').order_by('start_date')
    completed_challenges = Challenge.objects.filter(
        status='completed').order_by('-end_date')

    # Get user's participations
    user_participations = ChallengeParticipation.objects.filter(
        user=request.user
    ).values_list('challenge_id', flat=True)

    context = {
        'active_challenges': active_challenges,
        'upcoming_challenges': upcoming_challenges,
        'completed_challenges': completed_challenges,
        'user_participations': user_participations
    }

    return render(request, 'healthxpfront/challenge_list.html', context)


@login_required
def challenge_detail(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)

    # Check if user is participating
    try:
        participation = ChallengeParticipation.objects.get(
            user=request.user, challenge=challenge)
        is_participating = True
    except ChallengeParticipation.DoesNotExist:
        participation = None
        is_participating = False

    # Count total participants
    total_participants = ChallengeParticipation.objects.filter(
        challenge=challenge).count()

    # Get leaderboard (top participants)
    leaderboard = ChallengeParticipation.objects.filter(
        challenge=challenge
    ).order_by('-current_progress', 'joined_at')[:10]

    # Handle join challenge form
    if request.method == 'POST' and challenge.status == 'active' and not is_participating:
        form = ChallengeParticipationForm(request.POST, user=request.user)
        if form.is_valid():
            ChallengeParticipation.objects.create(
                user=request.user,
                challenge=challenge,
                current_progress=0,
                completed=False
            )
            messages.success(
                request, f'You have joined the challenge: {challenge.title}!')
            return redirect('challenge_detail', pk=challenge.pk)
    else:
        form = ChallengeParticipationForm(
            initial={'challenge_id': challenge.pk}, user=request.user)

    context = {
        'challenge': challenge,
        'is_participating': is_participating,
        'participation': participation,
        'total_participants': total_participants,
        'leaderboard': leaderboard,
        'form': form
    }

    return render(request, 'healthxpfront/challenge_detail.html', context)


@login_required
def my_challenges(request):
    # Get user's challenge participations
    participations = ChallengeParticipation.objects.filter(
        user=request.user
    ).select_related('challenge').order_by('-challenge__status', '-challenge__end_date')

    # Separate by status
    active_participations = [
        p for p in participations if p.challenge.status == 'active']
    completed_participations = [
        p for p in participations if p.challenge.status == 'completed']

    context = {
        'active_participations': active_participations,
        'completed_participations': completed_participations
    }

    return render(request, 'healthxpfront/my_challenges.html', context)


@login_required
def reward_list(request):
    # Get rewards, filtering by point requirement
    affordable_rewards = Reward.objects.filter(
        is_active=True,
        available_quantity__gt=0,
        points_required__lte=request.user.profile.points
    ).order_by('points_required')

    unaffordable_rewards = Reward.objects.filter(
        is_active=True,
        available_quantity__gt=0,
        points_required__gt=request.user.profile.points
    ).order_by('points_required')

    # Calculate points needed for each unaffordable reward
    for reward in unaffordable_rewards:
        reward.points_needed = reward.points_required - request.user.profile.points

    # Get user's redemption history
    redemption_history = RewardRedemption.objects.filter(
        user=request.user
    ).select_related('reward').order_by('-created_at')

    context = {
        'affordable_rewards': affordable_rewards,
        'unaffordable_rewards': unaffordable_rewards,
        'redemption_history': redemption_history,
        'user_points': request.user.profile.points
    }

    return render(request, 'healthxpfront/reward_list.html', context)


@login_required
def reward_detail(request, pk):
    reward = get_object_or_404(Reward, pk=pk, is_active=True)

    if request.method == 'POST':
        if 'add_to_cart' in request.POST:
            # Get or create the user's shopping cart
            cart, created = ShoppingCart.objects.get_or_create(
                user=request.user)

            # Check if the item is already in the cart
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                reward=reward,
                defaults={'quantity': 1}
            )

            # If item already existed, increment the quantity
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()

            messages.success(request, f"{reward.name} added to your cart.")
            return redirect('cart_view')
        else:
            # Legacy direct redemption code (keeping for compatibility)
            form = RewardRedemptionForm(request.POST, user=request.user)
            if form.is_valid():
                redemption = form.save(commit=False)
                redemption.user = request.user
                redemption.reward = reward
                redemption.points_spent = reward.points_required
                redemption.save()

                # Update user points
                request.user.profile.points -= reward.points_required
                request.user.profile.save()

                # Update reward quantity
                reward.available_quantity -= 1
                reward.save()

                messages.success(
                    request, f'You have successfully redeemed {reward.name}!')
                return redirect('reward_list')
    else:
        form = RewardRedemptionForm(
            user=request.user, initial={'reward': reward})

    # Check if the user has a cart and if this reward is in it
    in_cart = False
    cart_quantity = 0
    try:
        cart = ShoppingCart.objects.get(user=request.user)
        cart_item = CartItem.objects.filter(cart=cart, reward=reward).first()
        if cart_item:
            in_cart = True
            cart_quantity = cart_item.quantity
    except ShoppingCart.DoesNotExist:
        pass

    context = {
        'reward': reward,
        'form': form,
        'can_afford': request.user.profile.points >= reward.points_required,
        'in_cart': in_cart,
        'cart_quantity': cart_quantity
    }

    return render(request, 'healthxpfront/reward_detail.html', context)


@login_required
def cart_view(request):
    """View to display and manage the user's shopping cart"""
    try:
        cart = ShoppingCart.objects.prefetch_related(
            'items__reward').get(user=request.user)
        cart_items = cart.items.all()

        # Calculate if user can afford entire cart
        can_afford_cart = request.user.profile.points >= cart.total_points
    except ShoppingCart.DoesNotExist:
        cart = None
        cart_items = []
        can_afford_cart = True

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'user_points': request.user.profile.points,
        'can_afford_cart': can_afford_cart
    }

    return render(request, 'healthxpfront/cart.html', context)


@login_required
def update_cart_item(request, item_id):
    """View to update cart item quantity or remove it"""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'increase':
            # Check if increasing would exceed available quantity
            if item.quantity < item.reward.available_quantity:
                item.quantity += 1
                item.save()
                messages.success(request, "Quantity increased.")
            else:
                messages.warning(
                    request, "Cannot increase quantity. Maximum available reached.")

        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
                messages.success(request, "Quantity decreased.")
            else:
                # If quantity is 1, remove the item
                item.delete()
                messages.success(request, "Item removed from cart.")

        elif action == 'remove':
            item.delete()
            messages.success(request, "Item removed from cart.")

    return redirect('cart_view')


@login_required
def checkout(request):
    """Process cart checkout and convert to redemptions"""
    try:
        cart = ShoppingCart.objects.prefetch_related(
            'items__reward').get(user=request.user)

        # Verify user can afford the cart
        total_points_needed = cart.total_points

        if request.user.profile.points < total_points_needed:
            messages.error(
                request, "You don't have enough points to complete this purchase.")
            return redirect('cart_view')

        # Process each item in the cart
        checkout_date = timezone.now()
        checkout_reference = f"CO-{request.user.id}-{int(checkout_date.timestamp())}"

        for item in cart.items.all():
            reward = item.reward

            # Check if reward is still available in requested quantity
            if reward.available_quantity < item.quantity:
                messages.error(
                    request, f"Sorry, {reward.name} is no longer available in the requested quantity.")
                return redirect('cart_view')

            # Create redemption entries for each quantity
            for _ in range(item.quantity):
                notes = f"Checkout Reference: {checkout_reference}\nPart of a cart checkout with {cart.total_items} item(s).\nTotal points spent: {total_points_needed}"

                redemption = RewardRedemption.objects.create(
                    user=request.user,
                    reward=reward,
                    points_spent=reward.points_required,
                    status='pending',
                    notes=notes
                )

                # Update reward quantity
                reward.available_quantity -= 1
                reward.save()

        # Deduct points from user profile
        request.user.profile.points -= total_points_needed
        request.user.profile.save()

        # Clear the cart after successful checkout
        cart.delete()

        messages.success(
            request, "Checkout completed successfully! Your rewards will be processed soon.")
        return redirect('redemption_history')

    except ShoppingCart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('reward_list')


@login_required
def leaderboard(request):
    # Get filter parameters
    time_period = request.GET.get('period', 'all-time')
    activity_type_id = request.GET.get('activity', 'all')
    page = request.GET.get('page', 1)

    # Base query for users with profiles
    users_query = Profile.objects.select_related('user').all()

    # Apply time period filter to activities
    if time_period != 'all-time':
        today = timezone.now().date()
        if time_period == 'this-week':
            start_date = today - datetime.timedelta(days=today.weekday())
        elif time_period == 'this-month':
            start_date = today.replace(day=1)
        elif time_period == 'this-year':
            start_date = today.replace(month=1, day=1)

        # Annotate users with filtered activity counts and points
        users_query = users_query.annotate(
            activities_count=Count(
                'user__activities',
                filter=Q(user__activities__date__gte=start_date),
                distinct=True
            ),
            period_points=Coalesce(
                Sum(
                    'user__activities__points_earned',
                    filter=Q(user__activities__date__gte=start_date)
                ),
                0
            )
        )
    else:
        # Annotate users with total activity counts
        users_query = users_query.annotate(
            activities_count=Count('user__activities', distinct=True),
            # Use total points for all-time
            period_points=Coalesce(F('points'), 0)
        )

    # Apply activity type filter
    if activity_type_id != 'all':
        users_query = users_query.filter(
            user__activities__activity_type_id=activity_type_id
        ).distinct()

    # Exclude users with 0 points and 0 activities
    users_query = users_query.filter(
        Q(period_points__gt=0) | Q(activities_count__gt=0)
    )

    # Order by points and get top users
    users_query = users_query.order_by(
        '-period_points', '-activities_count', 'user__date_joined')

    # Get activity types for the filter dropdown
    activity_types = ActivityType.objects.filter(is_active=True)

    # Implement pagination
    paginator = Paginator(users_query, 20)  # Show 20 users per page
    try:
        leaderboard_page = paginator.page(page)
    except PageNotAnInteger:
        leaderboard_page = paginator.page(1)
    except EmptyPage:
        leaderboard_page = paginator.page(paginator.num_pages)

    # Get user's ranking
    try:
        user_rank = list(users_query.values_list(
            'user_id', flat=True)).index(request.user.id) + 1
    except ValueError:
        user_rank = None

    # Prepare leaderboard entries with rank numbers
    leaderboard_entries = []
    start_rank = (leaderboard_page.number - 1) * paginator.per_page + 1

    for idx, profile in enumerate(leaderboard_page):
        entry = {
            'rank': start_rank + idx,
            'user': profile.user,
            'points': profile.period_points or 0,
            'activities_count': profile.activities_count or 0,
            'profile': profile,
            'member_since': profile.user.date_joined
        }
        leaderboard_entries.append(entry)

    context = {
        'top_users': users_query[:3],  # Get top 3 users for special display
        'leaderboard': leaderboard_page,
        'leaderboard_entries': leaderboard_entries,
        'user_rank': user_rank,
        'activity_types': activity_types,
        'time_period': time_period,
        'activity_type': activity_type_id,
        'total_participants': users_query.count()
    }

    return render(request, 'healthxpfront/leaderboard.html', context)


# Helper function to update challenge progress
def update_challenge_progress(user, activity_type, increment=1):
    # Find all active challenges the user is participating in that match this activity type
    participations = ChallengeParticipation.objects.filter(
        user=user,
        challenge__status='active',
        challenge__activity_type=activity_type,
        completed=False
    )

    for participation in participations:
        # Update progress
        participation.current_progress += increment

        # Check if challenge is completed
        if participation.current_progress >= participation.challenge.target_count:
            participation.completed = True
            participation.completed_at = timezone.now()

            # Award points for completing the challenge
            user.profile.points += participation.challenge.points_reward
            user.profile.save()

            # Send notification or message (implement later)

        # Save changes
        participation.save()


@login_required
def connect_fitness_device(request, provider):
    """View to initiate fitness device connection"""
    from django.conf import settings

    # List of supported providers
    supported_providers = ['fitbit', 'googlefit', 'strava']

    if provider not in supported_providers:
        messages.error(request, f"Unsupported fitness provider: {provider}")
        return redirect('profile')

    # For demonstration, we'll just create a placeholder connection
    # In a real app, this would redirect to the OAuth flow

    # Check if connection already exists
    existing_connection = FitnessDeviceConnection.objects.filter(
        user=request.user,
        provider=provider
    ).first()

    if existing_connection:
        if existing_connection.is_active:
            messages.info(
                request, f"You already have an active connection to {provider}")
        else:
            # Reactivate
            existing_connection.is_active = True
            existing_connection.save()
            messages.success(request, f"Reconnected to {provider}")
        return redirect('profile')

    # Create a placeholder connection (in real app, this would be after OAuth)
    FitnessDeviceConnection.objects.create(
        user=request.user,
        provider=provider,
        access_token="placeholder_token",
        refresh_token="placeholder_refresh",
        is_active=True
    )

    messages.success(request, f"Successfully connected to {provider}")
    return redirect('profile')


@login_required
def disconnect_fitness_device(request, provider):
    """View to disconnect fitness device"""
    connection = get_object_or_404(
        FitnessDeviceConnection,
        user=request.user,
        provider=provider
    )

    connection.is_active = False
    connection.save()

    messages.success(request, f"Disconnected from {provider}")
    return redirect('profile')


@login_required
def sync_fitness_data(request):
    """View to manually trigger fitness data sync"""
    connections = FitnessDeviceConnection.objects.filter(
        user=request.user,
        is_active=True
    )

    if not connections:
        messages.warning(request, "No active fitness device connections found")
        return redirect('profile')

    sync_count = 0
    for connection in connections:
        if connection.provider == 'fitbit':
            success = sync_fitbit_data(connection)
            if success:
                sync_count += 1
        # Add more providers as needed

    if sync_count > 0:
        messages.success(
            request, f"Successfully synced data from {sync_count} fitness devices")
    else:
        messages.warning(
            request, "No data was synced from your fitness devices")

    return redirect('dashboard')


@login_required
def achievements(request):
    """View to display user achievements"""
    user_achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement').order_by('-date_earned')

    available_achievements = Achievement.objects.filter(
        is_active=True
    ).exclude(
        id__in=user_achievements.values_list('achievement_id', flat=True)
    )

    context = {
        'user_achievements': user_achievements,
        'available_achievements': available_achievements
    }

    return render(request, 'healthxpfront/achievements.html', context)


@login_required
def health_metrics(request):
    """View to display user health metrics history"""
    metrics = HealthMetric.objects.filter(
        user=request.user
    ).order_by('-date')

    # Calculate averages
    last_week = timezone.now().date() - datetime.timedelta(days=7)
    weekly_metrics = HealthMetric.objects.filter(
        user=request.user,
        date__gte=last_week
    )

    avg_steps = weekly_metrics.aggregate(Avg('steps'))['steps__avg']
    avg_sleep = weekly_metrics.aggregate(Avg('sleep_duration'))[
        'sleep_duration__avg']
    avg_heart_rate = weekly_metrics.aggregate(
        Avg('heart_rate'))['heart_rate__avg']

    context = {
        'metrics': metrics,
        'avg_steps': avg_steps,
        'avg_sleep': avg_sleep,
        'avg_heart_rate': avg_heart_rate
    }

    return render(request, 'healthxpfront/health_metrics.html', context)


@login_required
def redemption_history(request):
    """View to display detailed redemption history"""
    # Get status filter from query params
    status_filter = request.GET.get('status', '')

    # Base query for redemptions
    redemptions = RewardRedemption.objects.filter(
        user=request.user
    ).select_related('reward').order_by('-created_at')

    # Apply status filter if provided
    if status_filter and status_filter != 'all':
        redemptions = redemptions.filter(status=status_filter)

    # Calculate statistics
    total_points_spent = redemptions.aggregate(
        total=Sum('points_spent'))['total'] or 0
    total_redemptions = redemptions.count()
    status_counts = {
        'pending': redemptions.filter(status='pending').count(),
        'approved': redemptions.filter(status='approved').count(),
        'delivered': redemptions.filter(status='delivered').count(),
        'rejected': redemptions.filter(status='rejected').count()
    }

    context = {
        'redemptions': redemptions,
        'total_points_spent': total_points_spent,
        'total_redemptions': total_redemptions,
        'status_counts': status_counts,
        'current_filter': status_filter
    }

    return render(request, 'healthxpfront/redemption_history.html', context)


@login_required
def my_subscription(request):
    try:
        subscription = Subscription.objects.select_related(
            'subscription_type').get(user=request.user)
        subscription_history = Subscription.objects.filter(
            user=request.user
            # Exclude current subscription
        ).select_related('subscription_type').order_by('-start_date')[1:]
    except Subscription.DoesNotExist:
        subscription = None
        subscription_history = []

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'toggle_auto_renew' and subscription:
            subscription.auto_renew = not subscription.auto_renew
            subscription.save()
            messages.success(
                request,
                'Auto-renewal has been enabled.' if subscription.auto_renew else 'Auto-renewal has been disabled.'
            )

        elif action == 'cancel_subscription' and subscription:
            subscription.status = 'cancelled'
            subscription.end_date = timezone.now().date()
            subscription.auto_renew = False
            subscription.save()
            messages.success(request, 'Your subscription has been cancelled.')

        return redirect('my_subscription')

    context = {
        'subscription': subscription,
        'subscription_history': subscription_history,
    }

    return render(request, 'healthxpfront/my_subscriptions.html', context)
