from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import User, ResidentProfile, StaffProfile, LoginHistory
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileUpdateForm, ResidentProfileUpdateForm
from .decorators import admin_required

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


def get_device_type(user_agent):
    ua = user_agent.lower()
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        return 'Mobile Smartphone'
    elif 'ipad' in ua or 'tablet' in ua:
        return 'Tablet'
    return 'Desktop Workstation'


def login_view(request):
    """User login view with security session logging and credential validation."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Log login record
            ip = get_client_ip(request)
            ua = request.META.get('HTTP_USER_AGENT', 'Unknown')
            LoginHistory.objects.create(
                user=user,
                ip_address=ip,
                user_agent=ua,
                device_type=get_device_type(ua),
                is_successful=True
            )

            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}! Signed in as {user.get_role_display()}.")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please verify your credentials.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, "You have been safely signed out.")
    return redirect('accounts:login')


def register_view(request):
    """Resident & User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == User.Role.RESIDENT:
                ResidentProfile.objects.create(user=user)
            elif user.role == User.Role.STAFF:
                StaffProfile.objects.create(user=user)

            ip = get_client_ip(request)
            ua = request.META.get('HTTP_USER_AGENT', 'Unknown')
            LoginHistory.objects.create(
                user=user,
                ip_address=ip,
                user_agent=ua,
                device_type=get_device_type(ua),
                is_successful=True
            )

            login(request, user)
            messages.success(request, f"Welcome to Emerald Greens, {user.full_name}! Your resident account is ready.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the highlighted errors.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """User profile viewing and updating."""
    user = request.user
    resident_profile, _ = ResidentProfile.objects.get_or_create(user=user) if user.role == User.Role.RESIDENT else (None, False)

    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=user)
        res_form = ResidentProfileUpdateForm(request.POST, instance=resident_profile) if resident_profile else None

        if user_form.is_valid() and (not res_form or res_form.is_valid()):
            user_form.save()
            if res_form:
                res_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        user_form = UserProfileUpdateForm(instance=user)
        res_form = ResidentProfileUpdateForm(instance=resident_profile) if resident_profile else None

    flats = (user.resident_flats.all() | user.owned_units.all()).distinct()
    vehicles = user.vehicles.all()
    recent_logins = user.login_records.all()[:5]

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'res_form': res_form,
        'flats': flats,
        'vehicles': vehicles,
        'recent_logins': recent_logins,
    })


@login_required
def security_settings_view(request):
    """Change password and configure 2FA security preferences."""
    user = request.user
    if request.method == 'POST':
        if 'change_password' in request.POST:
            pwd_form = PasswordChangeForm(user, request.POST)
            if pwd_form.is_valid():
                user = pwd_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed successfully!")
                return redirect('accounts:security')
            else:
                messages.error(request, "Please correct the password errors.")
        elif 'update_2fa' in request.POST:
            two_factor = request.POST.get('two_factor_enabled') == 'on'
            pin = request.POST.get('security_pin', '1234')
            user.two_factor_enabled = two_factor
            user.security_pin = pin
            user.save()
            messages.success(request, "Security preferences updated.")
            return redirect('accounts:security')
    else:
        pwd_form = PasswordChangeForm(user)

    login_history = user.login_records.all()[:10]

    return render(request, 'accounts/security_settings.html', {
        'pwd_form': pwd_form,
        'login_history': login_history,
    })


@login_required
def demo_switch_user(request, role):
    """Role switch helper available only to authenticated users."""
    role = role.upper()
    user = User.objects.filter(role=role).first()
    if not user and role == 'ADMIN':
        user = User.objects.filter(is_superuser=True).first()

    if user:
        login(request, user)
        messages.success(request, f"Active Session Switched: {user.full_name} ({user.get_role_display()})")
    else:
        messages.warning(request, f"No user account found with role {role}.")

    return redirect('dashboard')
