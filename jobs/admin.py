from django.contrib import admin
from django import forms
from .models import Job, UserRoleSuggestion


class BulkRoleSuggestionForm(forms.Form):
    """Form for creating multiple role suggestions at once"""
    user = forms.ModelChoiceField(
        queryset=None,  # Set in __init__
        label="User/Client",
        help_text="Select the user to receive role suggestions"
    )
    role_titles = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 60, 'placeholder': 'Enter one role per line, e.g.:\nSoftware Engineer\nData Analyst\nBackend Developer\nML Engineer'}),
        label="Role Titles (one per line)",
        help_text="Enter 1-10 role titles, one per line. Each will create a separate suggestion."
    )
    role_category = forms.CharField(
        max_length=100,
        required=False,
        label="Category (optional)",
        help_text="Optional category for all roles (e.g., Engineering, Data Science)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Engineering'})
    )
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 60, 'placeholder': 'Optional notes explaining why these roles are suggested'}),
        required=False,
        label="Admin Notes (optional)",
        help_text="These notes will be applied to all role suggestions"
    )
    
    def __init__(self, *args, **kwargs):
        from django.contrib.auth.models import User
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_active=True).order_by('username')
    
    def clean_role_titles(self):
        """Validate role titles"""
        role_titles_text = self.cleaned_data['role_titles']
        
        # Split by newlines and clean
        roles = [line.strip() for line in role_titles_text.strip().split('\n') if line.strip()]
        
        if not roles:
            raise forms.ValidationError("Please enter at least one role title.")
        
        if len(roles) > 10:
            raise forms.ValidationError(f"Maximum 10 roles allowed. You entered {len(roles)} roles.")
        
        # Check for duplicates
        if len(roles) != len(set(roles)):
            raise forms.ValidationError("Duplicate role titles found. Please ensure each role is unique.")
        
        return roles


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'price', 'is_open')


@admin.register(UserRoleSuggestion)
class UserRoleSuggestionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing role suggestions
    Admins can type role titles directly - no predefined database needed
    """
    list_display = [
        'user', 'role_title', 'role_category', 'added_by', 'is_selected', 
        'selected_at', 'created_at'
    ]
    list_filter = ['is_selected', 'role_category', 'created_at']
    search_fields = ['user__username', 'user__email', 'role_title', 'role_category', 'admin_notes']
    readonly_fields = ['id', 'selected_at', 'created_at']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('User Selection', {
            'fields': ('user',),
            'description': 'Select the user/client for this role suggestion'
        }),
        ('Role Details', {
            'fields': ('role_title', 'role_category'),
            'description': 'Enter role title and optional category (e.g., Engineering, Marketing)'
        }),
        ('Admin Information', {
            'fields': ('added_by', 'admin_notes'),
            'description': 'Optional notes on why this role is suggested'
        }),
        ('User Selection Status', {
            'fields': ('is_selected', 'selected_at'),
            'classes': ('collapse',),
            'description': 'Automatically updated when user selects/deselects'
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['bulk_create_suggestions']
    
    def save_model(self, request, obj, form, change):
        """Auto-set added_by to current admin user"""
        if not change:  # Only on creation
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimize query with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'added_by')
    
    def get_urls(self):
        """Add custom URL for bulk creation"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_view), name='jobs_userrolesuggestion_bulk_create'),
        ]
        return custom_urls + urls
    
    def bulk_create_view(self, request):
        """View for bulk creating role suggestions"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        
        if request.method == 'POST':
            form = BulkRoleSuggestionForm(request.POST)
            if form.is_valid():
                created_count, skipped_count = self._create_bulk_suggestions(request, form)
                self._show_bulk_messages(request, created_count, skipped_count, form.cleaned_data['user'].username)
                return redirect('admin:jobs_userrolesuggestion_changelist')
        else:
            form = BulkRoleSuggestionForm()
        
        context = {
            'form': form,
            'title': 'Bulk Create Role Suggestions',
            'site_title': 'Hyrind Admin',
            'site_header': 'Hyrind Admin',
            'has_permission': True,
        }
        return render(request, 'admin/jobs/bulk_create_suggestions.html', context)
    
    def _create_bulk_suggestions(self, request, form):
        """Helper method to create bulk suggestions"""
        user = form.cleaned_data['user']
        role_titles = form.cleaned_data['role_titles']
        role_category = form.cleaned_data.get('role_category', '')
        admin_notes = form.cleaned_data.get('admin_notes', '')
        
        created_count = 0
        skipped_count = 0
        
        for role_title in role_titles:
            exists = UserRoleSuggestion.objects.filter(user=user, role_title=role_title).exists()
            
            if exists:
                skipped_count += 1
                continue
            
            UserRoleSuggestion.objects.create(
                user=user,
                role_title=role_title,
                role_category=role_category,
                admin_notes=admin_notes,
                added_by=request.user
            )
            created_count += 1
        
        return created_count, skipped_count
    
    def _show_bulk_messages(self, request, created_count, skipped_count, username):
        """Helper method to show bulk operation messages"""
        from django.contrib import messages
        
        if created_count > 0:
            messages.success(
                request,
                f"Successfully created {created_count} role suggestion(s) for {username}."
            )
        if skipped_count > 0:
            messages.warning(
                request,
                f"Skipped {skipped_count} duplicate role(s) that already exist."
            )
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }

    readonly_fields = ['id', 'created_at']
