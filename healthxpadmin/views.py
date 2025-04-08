from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from healthxpfront.models import (
    Profile, ActivityType, ActivityLog, Challenge, ChallengeParticipation,
    Reward, RewardRedemption, Subscription, SubscriptionType
)
from .forms import ProfileForm
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import models


@login_required
def dashboard_home(request):
    """Main dashboard view showing overview statistics"""
    context = {
        'total_users': User.objects.count(),
        'total_activities': ActivityType.objects.count(),
        'total_challenges': Challenge.objects.count(),
        'total_rewards': Reward.objects.count(),
        'total_subscriptions': Subscription.objects.count(),
        'total_subscription_types': SubscriptionType.objects.count(),
        'recent_activities': ActivityLog.objects.select_related('user', 'activity_type').order_by('-created_at')[:5],
        'recent_challenges': Challenge.objects.order_by('-created_at')[:5],
        'recent_rewards': Reward.objects.order_by('-created_at')[:5],
        'recent_subscriptions': Subscription.objects.select_related('user', 'subscription_type').order_by('-created_at')[:5],
    }
    return render(request, 'healthxpadmin/dashboard_home.html', context)


# User Management
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'healthxpadmin/user_list.html'
    context_object_name = 'users'
    paginate_by = 10


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    template_name = 'healthxpadmin/user_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('healthxpadmin:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create associated profile
        Profile.objects.create(user=self.object)
        return response


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'healthxpadmin/user_detail.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_activities'] = ActivityLog.objects.filter(
            user=self.object
        ).select_related('activity_type').order_by('-created_at')[:5]
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'healthxpadmin/user_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
    success_url = reverse_lazy('healthxpadmin:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = ProfileForm(
                self.request.POST, self.request.FILES, instance=self.object.profile)
        else:
            context['profile_form'] = ProfileForm(instance=self.object.profile)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        if profile_form.is_valid():
            self.object = form.save()
            profile_form.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'healthxpadmin/user_confirm_delete.html'
    success_url = reverse_lazy('healthxpadmin:user_list')


# Activity Management
class ActivityTypeListView(LoginRequiredMixin, ListView):
    model = ActivityType
    template_name = 'healthxpadmin/activity_type_list.html'
    context_object_name = 'activity_types'


class ActivityTypeCreateView(LoginRequiredMixin, CreateView):
    model = ActivityType
    template_name = 'healthxpadmin/activity_type_form.html'
    fields = ['name', 'description', 'icon_class', 'points', 'is_active']
    success_url = reverse_lazy('healthxpadmin:activity_type_list')


class ActivityTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = ActivityType
    template_name = 'healthxpadmin/activity_type_form.html'
    fields = ['name', 'description', 'icon_class', 'points', 'is_active']
    success_url = reverse_lazy('healthxpadmin:activity_type_list')


class ActivityTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = ActivityType
    template_name = 'healthxpadmin/activity_type_confirm_delete.html'
    success_url = reverse_lazy('healthxpadmin:activity_type_list')


# Activity Logs
class ActivityLogListView(LoginRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'healthxpadmin/activity_log_list.html'
    context_object_name = 'activity_logs'


class ActivityLogDetailView(LoginRequiredMixin, DetailView):
    model = ActivityLog
    template_name = 'healthxpadmin/activity_log_detail.html'
    context_object_name = 'activity_log'


# Challenge Management
class ChallengeListView(LoginRequiredMixin, ListView):
    model = Challenge
    template_name = 'healthxpadmin/challenge_list.html'
    context_object_name = 'challenges'


class ChallengeCreateView(LoginRequiredMixin, CreateView):
    model = Challenge
    template_name = 'healthxpadmin/challenge_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'target_count',
              'activity_type', 'points_reward', 'status', 'image', 'is_featured',
              'difficulty_level']
    success_url = reverse_lazy('healthxpadmin:challenge_list')


class ChallengeUpdateView(LoginRequiredMixin, UpdateView):
    model = Challenge
    template_name = 'healthxpadmin/challenge_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'target_count',
              'activity_type', 'points_reward', 'status', 'image', 'is_featured',
              'difficulty_level']
    success_url = reverse_lazy('healthxpadmin:challenge_list')


class ChallengeDeleteView(LoginRequiredMixin, DeleteView):
    model = Challenge
    template_name = 'healthxpadmin/challenge_confirm_delete.html'
    success_url = reverse_lazy('healthxpadmin:challenge_list')


# Reward Management
class RewardListView(LoginRequiredMixin, ListView):
    model = Reward
    template_name = 'healthxpadmin/reward_list.html'
    context_object_name = 'rewards'


class RewardCreateView(LoginRequiredMixin, CreateView):
    model = Reward
    template_name = 'healthxpadmin/reward_form.html'
    fields = ['name', 'description', 'points_required', 'image', 'available_quantity',
              'is_active', 'sponsor', 'category']
    success_url = reverse_lazy('healthxpadmin:reward_list')


class RewardUpdateView(LoginRequiredMixin, UpdateView):
    model = Reward
    template_name = 'healthxpadmin/reward_form.html'
    fields = ['name', 'description', 'points_required', 'image', 'available_quantity',
              'is_active', 'sponsor', 'category']
    success_url = reverse_lazy('healthxpadmin:reward_list')


class RewardDeleteView(LoginRequiredMixin, DeleteView):
    model = Reward
    template_name = 'healthxpadmin/reward_confirm_delete.html'
    success_url = reverse_lazy('healthxpadmin:reward_list')


# Subscription Type Management
class SubscriptionTypeListView(LoginRequiredMixin, ListView):
    model = SubscriptionType
    template_name = 'healthxpadmin/subscription_type_list.html'
    context_object_name = 'subscription_types'
    paginate_by = 10

    def get_queryset(self):
        queryset = SubscriptionType.objects.all()

        # Search by name or code
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(code__icontains=search_query)
            )

        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        # Sort by field
        sort_by = self.request.GET.get('sort', 'amount')
        if sort_by.startswith('-'):
            sort_by = sort_by[1:]
            queryset = queryset.order_by(f'-{sort_by}')
        else:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add subscription counts for each type
        for subscription_type in context['subscription_types']:
            subscription_type.subscriber_count = subscription_type.subscriptions.filter(
                status='active'
            ).count()
        return context


class SubscriptionTypeCreateView(LoginRequiredMixin, CreateView):
    model = SubscriptionType
    template_name = 'healthxpadmin/subscription_type_form.html'
    fields = ['name', 'code', 'description', 'amount', 'features', 'is_active']
    success_url = reverse_lazy('healthxpadmin:subscription_type_list')

    def form_valid(self, form):
        messages.success(
            self.request, f'Subscription type "{form.instance.name}" has been created successfully.')
        return super().form_valid(form)


class SubscriptionTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = SubscriptionType
    template_name = 'healthxpadmin/subscription_type_form.html'
    fields = ['name', 'code', 'description', 'amount', 'features', 'is_active']
    success_url = reverse_lazy('healthxpadmin:subscription_type_list')

    def form_valid(self, form):
        # Check if price has changed
        if form.instance.pk:
            old_instance = SubscriptionType.objects.get(pk=form.instance.pk)
            if old_instance.amount != form.cleaned_data['amount']:
                # Get active subscriptions for this type
                active_subscriptions = form.instance.subscriptions.filter(
                    status='active')
                active_count = active_subscriptions.count()

                if active_count > 0:
                    messages.warning(
                        self.request,
                        f'Price change will affect {active_count} active subscription(s). '
                        'Existing subscribers will be notified of the price change.'
                    )

        messages.success(
            self.request, f'Subscription type "{form.instance.name}" has been updated successfully.')
        return super().form_valid(form)


class SubscriptionTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = SubscriptionType
    template_name = 'healthxpadmin/subscription_type_confirm_delete.html'
    success_url = reverse_lazy('healthxpadmin:subscription_type_list')

    def delete(self, request, *args, **kwargs):
        subscription_type = self.get_object()
        if subscription_type.subscriptions.filter(status='active').exists():
            messages.error(
                request,
                'Cannot delete this subscription type because it has active subscriptions. '
                'Please deactivate it instead.'
            )
            return redirect('healthxpadmin:subscription_type_list')

        messages.success(
            request, f'Subscription type "{subscription_type.name}" has been deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Subscription Management
class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'healthxpadmin/subscription_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'user', 'user__profile', 'subscription_type')

        # Apply filters
        status = self.request.GET.get('status')
        subscription_type = self.request.GET.get('type')
        start_date_from = self.request.GET.get('start_date_from')
        start_date_to = self.request.GET.get('start_date_to')

        if status:
            queryset = queryset.filter(status=status)

        if subscription_type:
            queryset = queryset.filter(
                subscription_type__code=subscription_type)

        if start_date_from:
            queryset = queryset.filter(start_date__gte=start_date_from)

        if start_date_to:
            queryset = queryset.filter(start_date__lte=start_date_to)

        return queryset.order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscription_types'] = SubscriptionType.objects.filter(
            is_active=True)
        context['status_choices'] = Subscription.STATUS_CHOICES
        return context


class SubscriptionCreateView(LoginRequiredMixin, CreateView):
    model = Subscription
    template_name = 'healthxpadmin/subscription_form.html'
    fields = ['user', 'subscription_type', 'end_date', 'status', 'auto_renew']
    success_url = reverse_lazy('healthxpadmin:subscription_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['subscription_type'].queryset = SubscriptionType.objects.filter(
            is_active=True)
        return form

    def form_valid(self, form):
        return super().form_valid(form)


class SubscriptionDetailView(LoginRequiredMixin, DetailView):
    model = Subscription
    template_name = 'healthxpadmin/subscription_detail.html'
    context_object_name = 'subscription'


class SubscriptionUpdateView(LoginRequiredMixin, UpdateView):
    model = Subscription
    template_name = 'healthxpadmin/subscription_form.html'
    fields = ['subscription_type', 'end_date', 'status', 'auto_renew']
    success_url = reverse_lazy('healthxpadmin:subscription_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['subscription_type'].queryset = SubscriptionType.objects.filter(
            is_active=True)
        return form


class SubscriptionCancelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        subscription = get_object_or_404(Subscription, pk=kwargs['pk'])
        subscription.status = 'cancelled'
        subscription.end_date = timezone.now()
        subscription.save()

        messages.success(
            request, f'Subscription for {subscription.user.get_full_name() or subscription.user.username} has been cancelled.')
        return redirect('healthxpadmin:subscription_list')
