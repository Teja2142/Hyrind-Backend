from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, InterestSubmission, Contact, ClientIntakeSheet, CredentialSheet
from django.utils.html import format_html


# ============================================================================
# PROFILE (CLIENT) ADMIN
# ============================================================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for Client Profiles
    Comprehensive view of all client information with filtering and search
    """
    list_display = (
        'id_short',
        'full_name',
        'email',
        'phone',
        'active_status',
        'university',
        'major',
        'visa_status',
        'graduation_date',
        'has_resume',
        'created_date'
    )
    
    list_filter = (
        'active',
        'visa_status',
        'degree',
        'referral_source',
        'consent_to_terms',
        'graduation_date',
    )
    
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'phone',
        'university',
        'major',
        'user__email',
        'user__username',
    )
    
    readonly_fields = (
        'id',
        'user',
        'created_date',
        'resume_link',
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'active', 'email', 'phone')
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name')
        }),
        ('Education', {
            'fields': ('university', 'degree', 'major', 'graduation_date', 'opt_end_date')
        }),
        ('Immigration Status', {
            'fields': ('visa_status',)
        }),
        ('Documents & Links', {
            'fields': ('resume_file', 'resume_link', 'linkedin_url', 'github_url')
        }),
        ('Additional Information', {
            'fields': ('referral_source', 'consent_to_terms', 'additional_notes')
        }),
        ('Metadata', {
            'fields': ('created_date',),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 50
    date_hierarchy = 'user__date_joined'
    
    def id_short(self, obj):
        """Display shortened UUID"""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def full_name(self, obj):
        """Display full name with email fallback"""
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.email
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
    
    def active_status(self, obj):
        """Display active status with colored indicator"""
        if obj.active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
        )
    active_status.short_description = 'Status'
    active_status.admin_order_field = 'active'
    
    def has_resume(self, obj):
        """Indicate if resume is uploaded"""
        if obj.resume_file:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">-</span>')
    has_resume.short_description = 'Resume'
    
    def resume_link(self, obj):
        """Display resume download link"""
        if obj.resume_file:
            return format_html(
                '<a href="{}" target="_blank">Download Resume</a>',
                obj.resume_file.url
            )
        return '-'
    resume_link.short_description = 'Resume File'
    
    def created_date(self, obj):
        """Display user creation date"""
        if obj.user:
            return obj.user.date_joined.strftime('%Y-%m-%d %H:%M')
        return '-'
    created_date.short_description = 'Created Date'
    
    actions = ['activate_profiles', 'deactivate_profiles']
    
    def activate_profiles(self, request, queryset):
        """Bulk activate selected profiles"""
        updated = queryset.update(active=True)
        self.message_user(request, f'{updated} profile(s) activated successfully.')
    activate_profiles.short_description = 'Activate selected profiles'
    
    def deactivate_profiles(self, request, queryset):
        """Bulk deactivate selected profiles"""
        updated = queryset.update(active=False)
        self.message_user(request, f'{updated} profile(s) deactivated successfully.')
    deactivate_profiles.short_description = 'Deactivate selected profiles'


# ============================================================================
# INTEREST SUBMISSION ADMIN
# ============================================================================

@admin.register(InterestSubmission)
class InterestSubmissionAdmin(admin.ModelAdmin):
    """
    Admin interface for Interest Submissions (Pre-registration inquiries)
    """
    list_display = (
        'id_short',
        'created_at',
        'full_name',
        'email',
        'phone',
        'university',
        'degree',
        'major',
        'visa_status',
        'graduation_date',
        'has_resume',
    )
    
    list_filter = (
        'created_at',
        'visa_status',
        'degree',
        'referral_source',
        'consent_to_terms',
    )
    
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'phone',
        'university',
        'major',
    )
    
    readonly_fields = (
        'id',
        'created_at',
        'resume_link',
    )
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('id', 'created_at')
        }),
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Education Details', {
            'fields': ('university', 'degree', 'major', 'graduation_date', 'opt_end_date')
        }),
        ('Immigration Status', {
            'fields': ('visa_status',)
        }),
        ('Documents & Links', {
            'fields': ('resume_file', 'resume_link', 'linkedin_url', 'github_url')
        }),
        ('Additional Information', {
            'fields': ('referral_source', 'consent_to_terms', 'additional_notes')
        }),
    )
    
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def id_short(self, obj):
        """Display shortened UUID"""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}".strip()
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
    
    def has_resume(self, obj):
        """Indicate if resume is uploaded"""
        if obj.resume_file:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">-</span>')
    has_resume.short_description = 'Resume'
    
    def resume_link(self, obj):
        """Display resume download link"""
        if obj.resume_file:
            return format_html(
                '<a href="{}" target="_blank">Download Resume</a>',
                obj.resume_file.url
            )
        return '-'
    resume_link.short_description = 'Resume File'


# ============================================================================
# CONTACT SUBMISSION ADMIN
# ============================================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface for Contact Form Submissions
    """
    list_display = (
        'created_at',
        'full_name',
        'email',
        'phone',
        'responded_status',
        'message_preview',
    )
    
    list_filter = (
        'responded',
        'created_at',
    )
    
    search_fields = (
        'full_name',
        'email',
        'phone',
        'message',
    )
    
    readonly_fields = (
        'created_at',
        'full_name',
        'email',
        'phone',
        'message',
    )
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone', 'created_at')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Response Status', {
            'fields': ('responded',)
        }),
    )
    
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def responded_status(self, obj):
        """Display responded status with colored indicator"""
        if obj.responded:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Responded</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
        )
    responded_status.short_description = 'Status'
    responded_status.admin_order_field = 'responded'
    
    def message_preview(self, obj):
        """Display first 50 characters of message"""
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message
    message_preview.short_description = 'Message Preview'
    
    actions = ['mark_as_responded', 'mark_as_pending']
    
    def mark_as_responded(self, request, queryset):
        """Mark selected contacts as responded"""
        updated = queryset.update(responded=True)
        self.message_user(request, f'{updated} contact(s) marked as responded.')
    mark_as_responded.short_description = 'Mark as responded'
    
    def mark_as_pending(self, request, queryset):
        """Mark selected contacts as pending"""
        updated = queryset.update(responded=False)
        self.message_user(request, f'{updated} contact(s) marked as pending.')
    mark_as_pending.short_description = 'Mark as pending'


# ============================================================================
# USER ADMIN (Enhanced)
# ============================================================================

class ProfileInline(admin.StackedInline):
    """Inline profile editor in User admin"""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('first_name', 'last_name', 'email', 'phone', 'active', 'university', 'major', 'visa_status')


class CustomUserAdmin(BaseUserAdmin):
    """Enhanced User admin with profile information"""
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ============================================================================
# CLIENT INTAKE SHEET ADMIN
# ============================================================================

@admin.register(ClientIntakeSheet)
class ClientIntakeSheetAdmin(admin.ModelAdmin):
    """
    Admin interface for Client Intake Sheets
    View of all client intake form submissions
    """
    list_display = (
        'id_short',
        'full_name',
        'email',
        'visa_status',
        'profile_link',
        'submitted_status',
        'submission_timestamp',
        'editable_status'
    )
    
    list_filter = (
        'visa_status',
        'is_editable',
        'submission_timestamp',
    )
    
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'visa_status',
    )
    
    readonly_fields = (
        'id',
        'submission_timestamp',
        'form_submitted_date',
        'profile',
    )
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('profile', 'id', 'first_name', 'last_name', 'date_of_birth', 'phone_number', 'email', 'alternate_email')
        }),
        ('Contact Information', {
            'fields': ('marketing_contact_number', 'marketing_email', 'current_address', 'mailing_address')
        }),
        ('Visa & Immigration', {
            'fields': ('visa_status', 'first_entry_us', 'total_years_in_us')
        }),
        ('Skills', {
            'fields': ('skilled_in', 'currently_learning', 'experienced_with', 'learning_tools', 'non_technical_skills'),
            'classes': ('collapse',)
        }),
        ('Work Experience', {
            'fields': (
                'job_1_title', 'job_1_company', 'job_1_address', 'job_1_start_date', 'job_1_end_date', 'job_1_type', 'job_1_responsibilities',
                'job_2_title', 'job_2_company', 'job_2_address', 'job_2_start_date', 'job_2_end_date', 'job_2_type', 'job_2_responsibilities',
                'job_3_title', 'job_3_company', 'job_3_address', 'job_3_start_date', 'job_3_end_date', 'job_3_type', 'job_3_responsibilities',
            ),
            'classes': ('collapse',)
        }),
        ('Education', {
            'fields': (
                'highest_degree', 'highest_field_of_study', 'highest_university', 'highest_country', 'highest_graduation_date',
                'bachelors_degree', 'bachelors_field_of_study', 'bachelors_university', 'bachelors_country', 'bachelors_graduation_date',
            ),
            'classes': ('collapse',)
        }),
        ('Certifications', {
            'fields': ('certification_name', 'issuing_organization', 'issued_date'),
            'classes': ('collapse',)
        }),
        ('Documents', {
            'fields': ('passport_file', 'government_id_file', 'visa_file', 'work_authorization_file', 'resume_file'),
        }),
        ('Job Preferences', {
            'fields': ('desired_job_role', 'desired_years_experience')
        }),
        ('Form Status', {
            'fields': ('submission_timestamp', 'form_submitted_date', 'is_editable')
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8] + '...'
    id_short.short_description = 'ID'
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/users/profile/{}/change/">{}</a>',
            obj.profile.id,
            obj.profile.first_name + ' ' + obj.profile.last_name
        )
    profile_link.short_description = 'Profile'
    
    def submitted_status(self, obj):
        if obj.submission_timestamp:
            return format_html(
                '<span style="color: green;">✓ Submitted</span>'
            )
        return format_html(
            '<span style="color: orange;">⊘ Draft</span>'
        )
    submitted_status.short_description = 'Status'
    
    def editable_status(self, obj):
        if obj.is_editable:
            return format_html(
                '<span style="color: blue;">Editable</span>'
            )
        return format_html(
            '<span style="color: red;">Locked</span>'
        )
    editable_status.short_description = 'Editable'


# ============================================================================
# CREDENTIAL SHEET ADMIN
# ============================================================================

@admin.register(CredentialSheet)
class CredentialSheetAdmin(admin.ModelAdmin):
    """
    Admin interface for Credential Sheets
    View of all credential form submissions with job platform credentials
    """
    list_display = (
        'id_short',
        'full_name',
        'personal_email',
        'profile_link',
        'submitted_status',
        'submission_timestamp',
        'editable_status'
    )
    
    list_filter = (
        'is_editable',
        'submission_timestamp',
    )
    
    search_fields = (
        'full_name',
        'personal_email',
        'phone_number',
        'location',
    )
    
    readonly_fields = (
        'id',
        'submission_timestamp',
        'form_submitted_date',
        'profile',
    )
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('profile', 'id', 'full_name', 'personal_email', 'phone_number', 'location')
        }),
        ('Education & OPT', {
            'fields': (
                'bachelor_graduation_date', 'first_entry_us', 'masters_graduation_date',
                'opt_start_date', 'opt_offer_letter_submitted', 'opt_offer_letter_file'
            )
        }),
        ('Job Preferences', {
            'fields': ('preferred_job_roles', 'preferred_locations')
        }),
        ('Platform Credentials', {
            'fields': (
                'linkedin_username', 'linkedin_password',
                'indeed_username', 'indeed_password',
                'dice_username', 'dice_password',
                'monster_username', 'monster_password',
                'ziprecruiter_username', 'ziprecruiter_password',
                'glassdoor_username', 'glassdoor_password',
                'buildin_username', 'buildin_password',
                'jobvite_username', 'jobvite_password',
                'careerbuilder_username', 'careerbuilder_password',
                'github_username', 'github_password',
                'other_job_platform_accounts',
            ),
            'classes': ('collapse',),
            'description': 'Job platform login credentials (stored securely)'
        }),
        ('Form Status', {
            'fields': ('submission_timestamp', 'form_submitted_date', 'is_editable')
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8] + '...'
    id_short.short_description = 'ID'
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/users/profile/{}/change/">{}</a>',
            obj.profile.id,
            obj.profile.first_name + ' ' + obj.profile.last_name
        )
    profile_link.short_description = 'Profile'
    
    def submitted_status(self, obj):
        if obj.submission_timestamp:
            return format_html(
                '<span style="color: green;">✓ Submitted</span>'
            )
        return format_html(
            '<span style="color: orange;">⊘ Draft</span>'
        )
    submitted_status.short_description = 'Status'
    
    def editable_status(self, obj):
        if obj.is_editable:
            return format_html(
                '<span style="color: blue;">Editable</span>'
            )
        return format_html(
            '<span style="color: red;">Locked</span>'
        )
    editable_status.short_description = 'Editable'