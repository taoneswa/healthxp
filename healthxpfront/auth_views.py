from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse


class CustomLoginView(LoginView):
    def get_success_url(self):
        # Check if user is staff/admin
        if self.request.user.is_staff:
            return reverse('healthxpadmin:dashboard_home')
        # Regular users go to the frontend dashboard
        return reverse('dashboard')
