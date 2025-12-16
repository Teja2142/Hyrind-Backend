from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .forms import RecruiterMinimalRegistrationForm, RecruiterProfileUpdateForm, RecruiterBasicUpdateForm
from users.models import Profile
from .models import Recruiter, RecruiterRegistration, Assignment


def recruiter_registration_view(request):
    """
    Minimal registration for internal IT recruitment staff.
    
    Creates User + Profile + Recruiter with:
    - AUTO-GENERATED Employee ID (H + 5 digits)
    - Basic info: email, name, phone, department, specialization, date of joining
    - Account status set to 'pending' (requires admin approval)
    - Profile completion required after login
    """
    if request.method == 'POST':
        form = RecruiterMinimalRegistrationForm(request.POST)
        if form.is_valid():
            recruiter = form.save()
            messages.success(
                request,
                f'✅ Registration Successful!<br>'
                f'Your Employee ID: <strong>{recruiter.employee_id}</strong><br>'
                f'Department: {recruiter.get_department_display()}<br>'
                f'Specialization: {recruiter.get_specialization_display()}<br><br>'
                f'<strong>Important:</strong> Your account is pending admin approval. '
                f'After approval, please complete your profile with additional details.'
            )
            return redirect('recruiter-login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterMinimalRegistrationForm()

    return render(request, 'recruiter_registration_form.html', {
        'form': form,
        'page_title': 'Recruiter Registration - Hyrind'
    })


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
            return redirect('recruiter-dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'recruiter_login.html')


@login_required
def recruiter_profile_view(request):
    """Allow logged-in recruiter to update basic info."""
    try:
        profile = Profile.objects.get(user=request.user)
        recruiter = Recruiter.objects.get(user=profile)
    except (Profile.DoesNotExist, Recruiter.DoesNotExist):
        messages.error(request, 'Recruiter profile not found for your account.')
        return redirect('home')

    if request.method == 'POST':
        form = RecruiterBasicUpdateForm(request.POST, instance=recruiter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('recruiter-profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterBasicUpdateForm(instance=recruiter)

    return render(request, 'recruiter_profile.html', {'form': form, 'recruiter': recruiter})


@login_required
def recruiter_complete_profile_view(request):
    """
    Comprehensive profile completion form.
    Collects personal details, address, ID proofs, education, bank details.
    """
    try:
        profile = Profile.objects.get(user=request.user)
        recruiter = Recruiter.objects.get(user=profile)
    except (Profile.DoesNotExist, Recruiter.DoesNotExist):
        messages.error(request, 'Recruiter profile not found.')
        return redirect('home')
    
    # Get or create RecruiterRegistration instance
    try:
        reg = RecruiterRegistration.objects.get(email=recruiter.email)
    except RecruiterRegistration.DoesNotExist:
        reg = None
    
    if request.method == 'POST':
        form = RecruiterProfileUpdateForm(request.POST, request.FILES, instance=reg, recruiter=recruiter)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.is_verified = True
            registration.save()
            messages.success(request, '✅ Profile completed successfully!')
            return redirect('recruiter-dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterProfileUpdateForm(instance=reg, recruiter=recruiter)
    
    return render(request, 'recruiter_complete_profile.html', {
        'form': form,
        'recruiter': recruiter,
        'page_title': 'Complete Your Profile'
    })


def recruiter_logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('home')


@login_required
def recruiter_dashboard_view(request):
    """
    Enhanced recruiter dashboard showing:
    - Profile completion status
    - Assigned clients
    - Performance stats
    - Quick actions
    """
    try:
        profile = Profile.objects.get(user=request.user)
        recruiter = Recruiter.objects.get(user=profile)
    except (Profile.DoesNotExist, Recruiter.DoesNotExist):
        messages.error(request, 'Recruiter profile not found for your account.')
        return redirect('home')

    # Check profile completion
    try:
        registration = RecruiterRegistration.objects.get(email=recruiter.email)
        profile_complete = registration.is_verified
    except RecruiterRegistration.DoesNotExist:
        profile_complete = False
        registration = None
    
    # Get assigned clients
    assignments = Assignment.objects.filter(recruiter=recruiter).select_related('profile')
    active_assignments = assignments.filter(status='active')
    placed_assignments = assignments.filter(status='placed')
    
    # Calculate stats
    stats = {
        'total_clients': recruiter.current_clients_count,
        'available_slots': recruiter.get_available_slots(),
        'total_placements': recruiter.total_placements,
        'active_applications': recruiter.active_applications,
        'profile_complete': profile_complete,
    }

    return render(request, 'recruiter_dashboard.html', {
        'recruiter': recruiter,
        'assignments': active_assignments,
        'placed_assignments': placed_assignments,
        'stats': stats,
        'profile_complete': profile_complete,
    })
