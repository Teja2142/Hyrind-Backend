from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .forms import RecruiterRegistrationFormModel, RecruiterRegistrationForm, RecruiterUpdateForm
from users.models import Profile
from .models import Recruiter


def recruiter_registration_form_view(request):
    """Render and process the recruiter registration template form."""
    if request.method == 'POST':
        form = RecruiterRegistrationFormModel(request.POST, request.FILES)
        if form.is_valid():
            registration = form.save()
            messages.success(request, 'Registration submitted successfully. We will verify and contact you soon.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterRegistrationFormModel()

    return render(request, 'recruiter_registration_form.html', {'form': form})


def recruiter_register_simple_view(request):
    """Simple user/recruiter account registration (creates User/Profile/Recruiter)."""
    if request.method == 'POST':
        form = RecruiterRegistrationForm(request.POST)
        if form.is_valid():
            recruiter = form.save()
            messages.success(request, 'Account created. Please wait for admin approval to activate your recruiter account.')
            return redirect('recruiter-login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterRegistrationForm()

    return render(request, 'recruiter_register_simple.html', {'form': form})


def recruiter_login_view(request):
    """Simple login page for recruiters using email and password."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Authenticate by email
        try:
            from django.contrib.auth.models import User
            user_obj = User.objects.get(email=email)
            user_auth = authenticate(username=user_obj.username, password=password)
        except Exception:
            user_auth = None

        if user_auth:
            # Ensure associated recruiter is active
            try:
                profile = Profile.objects.get(user=user_auth)
                recruiter = Recruiter.objects.get(user=profile)
                if not recruiter.active:
                    messages.error(request, 'Your recruiter account is not active yet. Please contact the administrator.')
                    return redirect('recruiter-login')
            except Exception:
                # If there's no recruiter record, allow login to proceed but warn
                pass

            login(request, user_auth)
            messages.success(request, 'Logged in successfully')
            return redirect('recruiter-profile')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'recruiter_login.html')


@login_required
def recruiter_profile_view(request):
    """Allow logged-in recruiter to view and update their recruiter profile."""
    try:
        profile = Profile.objects.get(user=request.user)
        recruiter = Recruiter.objects.get(user=profile)
    except (Profile.DoesNotExist, Recruiter.DoesNotExist):
        messages.error(request, 'Recruiter profile not found for your account.')
        return redirect('home')

    if request.method == 'POST':
        form = RecruiterUpdateForm(request.POST, instance=recruiter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('recruiter-profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterUpdateForm(instance=recruiter)

    return render(request, 'recruiter_profile.html', {'form': form, 'recruiter': recruiter})


def recruiter_logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('home')


@login_required
def recruiter_dashboard_view(request):
    """Simple recruiter dashboard showing assignments and quick stats."""
    try:
        profile = Profile.objects.get(user=request.user)
        recruiter = Recruiter.objects.get(user=profile)
    except (Profile.DoesNotExist, Recruiter.DoesNotExist):
        messages.error(request, 'Recruiter profile not found for your account.')
        return redirect('home')

    # Import here to avoid circular imports at module load
    from .models import Assignment
    assignments = Assignment.objects.filter(recruiter=recruiter)

    stats = {
        'total_assignments': assignments.count(),
    }

    return render(request, 'recruiter_dashboard.html', {
        'recruiter': recruiter,
        'assignments': assignments,
        'stats': stats,
    })
