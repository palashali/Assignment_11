from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('properties:property_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role_name = user.get_role_display()
            messages.success(request, f"Welcome to RentalHub, {user.username}! Your account has been created as {role_name}.")
            login(request, user)
            if user.is_owner:
                return redirect('rentals:owner_dashboard')
            return redirect('properties:property_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_owner:
            return redirect('rentals:owner_dashboard')
        return redirect('properties:property_list')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_owner:
                return redirect('rentals:owner_dashboard')
            return redirect('properties:property_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    if request.method in ['POST', 'GET']:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been successfully updated.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Failed to update profile. Please verify your input.")
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form,
        'user_obj': request.user
    }
    return render(request, 'accounts/profile.html', context)
