from django.contrib import admin
from .models import Recruiter, Assignment
from .models import RecruiterRegistration
from django.core.mail import send_mail
from django.conf import settings

@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'email')
    actions = ['activate_recruiters', 'deactivate_recruiters', 'export_selected']

    def activate_recruiters(self, request, queryset):
        activated = 0
        for r in queryset:
            try:
                # enable recruiter record
                r.active = True
                r.status = 'active'
                r.save(update_fields=['active', 'status'])
                # enable underlying user/profile
                profile = r.user
                try:
                    django_user = profile.user
                    django_user.is_active = True
                    django_user.save(update_fields=['is_active'])
                except Exception:
                    pass
                try:
                    profile.active = True
                    profile.save(update_fields=['active'])
                except Exception:
                    pass
                activated += 1
            except Exception:
                continue
        self.message_user(request, f"Activated {activated} recruiters")
    activate_recruiters.short_description = 'Activate selected recruiters'

    def deactivate_recruiters(self, request, queryset):
        deactivated = 0
        for r in queryset:
            try:
                r.active = False
                r.status = 'inactive'
                r.save(update_fields=['active', 'status'])
                profile = r.user
                try:
                    django_user = profile.user
                    django_user.is_active = False
                    django_user.save(update_fields=['is_active'])
                except Exception:
                    pass
                try:
                    profile.active = False
                    profile.save(update_fields=['active'])
                except Exception:
                    pass
                deactivated += 1
            except Exception:
                continue
        self.message_user(request, f"Deactivated {deactivated} recruiters")
    deactivate_recruiters.short_description = 'Deactivate selected recruiters'

    def export_selected(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=recruiters.csv'
        writer = csv.writer(response)
        writer.writerow(['id', 'name', 'email', 'phone', 'active'])
        for r in queryset:
            writer.writerow([r.id, r.name, r.email, r.phone, r.active])
        return response
    export_selected.short_description = 'Export selected recruiters to CSV'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'recruiter', 'assigned_at')
    search_fields = ('profile__first_name', 'profile__last_name', 'profile__email', 'recruiter__name')


@admin.register(RecruiterRegistration)
class RecruiterRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('full_name', 'email', 'aadhaar_number', 'pan_number')
    actions = ['verify_and_create_account']

    def verify_and_create_account(self, request, queryset):
        """Admin action to mark selected registrations as verified and create accounts."""
        created = 0
        for reg in queryset:
            if not reg.is_verified:
                reg.is_verified = True
                reg.save()
                # Auto-create user/profile/recruiter (reuse the logic from views)
                try:
                    from django.contrib.auth import get_user_model
                    from users.models import Profile
                    from .models import Recruiter

                    UserModel = get_user_model()
                    if not UserModel.objects.filter(email=reg.email).exists():
                        random_password = UserModel.objects.make_random_password()
                        user = UserModel.objects.create_user(
                            username=reg.email,
                            email=reg.email,
                            password=random_password,
                            first_name=(reg.full_name.split(' ')[0] if reg.full_name else ''),
                            last_name=(' '.join(reg.full_name.split(' ')[1:]) if reg.full_name and len(reg.full_name.split(' '))>1 else '')
                        )
                        # keep the account inactive until admin explicitly activates
                        user.is_active = False
                        user.save(update_fields=['is_active'])
                    else:
                        user = UserModel.objects.filter(email=reg.email).first()

                    profile, _ = Profile.objects.get_or_create(
                        user=user,
                        defaults={'first_name': (reg.full_name.split(' ')[0] if reg.full_name else ''),
                                  'last_name': (' '.join(reg.full_name.split(' ')[1:]) if reg.full_name and len(reg.full_name.split(' '))>1 else ''),
                                  'email': reg.email,
                                  'phone': reg.phone_number}
                    )

                    if not Recruiter.objects.filter(email=reg.email).exists():
                        Recruiter.objects.create(
                            user=profile,
                            name=reg.full_name,
                            email=reg.email,
                            phone=reg.phone_number,
                            active=False,
                        )

                    # send informational email (if email configured)
                    try:
                        send_mail(
                            'Your recruiter account has been created',
                            f'Hello {reg.full_name}, your registration has been approved. Please use your email to log in and reset your password if needed.',
                            settings.DEFAULT_FROM_EMAIL,
                            [reg.email],
                            fail_silently=True
                        )
                    except Exception:
                        pass

                    created += 1
                except Exception:
                    # continue with others
                    continue

        self.message_user(request, f"Verified {queryset.count()} registrations, created {created} accounts.")
    verify_and_create_account.short_description = 'Verify registrations and create accounts'
