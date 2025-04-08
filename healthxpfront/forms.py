from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, ActivityLog, ActivityType, Challenge, ChallengeParticipation, Reward, RewardRedemption, Subscription, Contact
import datetime


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), required=False)

    class Meta:
        model = Profile
        fields = ['profile_picture', 'birth_date', 'height', 'weight']


class ActivityLogForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today
    )

    class Meta:
        model = ActivityLog
        fields = ['activity_type', 'date', 'duration',
                  'distance', 'calories', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(ActivityLogForm, self).__init__(*args, **kwargs)
        # Only show active activity types
        self.fields['activity_type'].queryset = ActivityType.objects.filter(
            is_active=True)

        # Add 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True, user=None):
        instance = super(ActivityLogForm, self).save(commit=False)

        if user:
            instance.user = user

        # Calculate points earned based on activity type
        activity_points = instance.activity_type.points

        # Bonus points based on duration or distance
        bonus_points = 0
        if instance.duration and instance.duration >= 60:  # If duration >= 60 minutes
            bonus_points += 5
        if instance.distance and instance.distance >= 5:  # If distance >= 5 km
            bonus_points += 5

        instance.points_earned = activity_points + bonus_points

        if commit:
            instance.save()
            # Update user's total points
            if user:
                user.profile.points += instance.points_earned
                user.profile.save()

        return instance


class ChallengeParticipationForm(forms.Form):
    challenge_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChallengeParticipationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        challenge_id = cleaned_data.get('challenge_id')

        if challenge_id:
            try:
                challenge = Challenge.objects.get(pk=challenge_id)

                # Check if user is already participating
                if self.user and ChallengeParticipation.objects.filter(user=self.user, challenge=challenge).exists():
                    raise forms.ValidationError(
                        "You are already participating in this challenge.")

                # Check if challenge is active
                if challenge.status != 'active':
                    raise forms.ValidationError(
                        "This challenge is not currently active.")

            except Challenge.DoesNotExist:
                raise forms.ValidationError("Invalid challenge selected.")

        return cleaned_data


class RewardRedemptionForm(forms.ModelForm):
    class Meta:
        model = RewardRedemption
        fields = ['reward', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requests or delivery instructions?'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(RewardRedemptionForm, self).__init__(*args, **kwargs)

        # Only show active rewards with available quantity
        self.fields['reward'].queryset = Reward.objects.filter(
            is_active=True, available_quantity__gt=0)

        # Add 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        reward = cleaned_data.get('reward')

        if reward and self.user:
            # Check if user has enough points
            if self.user.profile.points < reward.points_required:
                raise forms.ValidationError(
                    f"You don't have enough points to redeem this reward. You need {reward.points_required} points.")

            # Check if reward is still available
            if reward.available_quantity <= 0:
                raise forms.ValidationError("This reward is out of stock.")

        return cleaned_data

    def save(self, commit=True):
        instance = super(RewardRedemptionForm, self).save(commit=False)

        if self.user:
            instance.user = self.user
            instance.points_spent = instance.reward.points_required

        if commit:
            # Deduct points from user
            self.user.profile.points -= instance.points_spent
            self.user.profile.save()

            # Reduce available quantity of reward
            instance.reward.available_quantity -= 1
            instance.reward.save()

            instance.save()

        return instance


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['subscription_type', 'auto_renew']

    def __init__(self, *args, **kwargs):
        super(SubscriptionForm, self).__init__(*args, **kwargs)

        # Add 'form-control' class to all fields
        for field_name, field in self.fields.items():
            if field_name != 'auto_renew':  # Don't add to checkboxes
                field.widget.attrs['class'] = 'form-control'


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your Message'}),
        }
