from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from .models import Subscription, SubscriptionPlan, UserSubscription, BillingHistory


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Admin interface for managing subscription plans"""
    list_display = ('name', 'plan_type_badge', 'base_price_display', 'billing_cycle', 'is_mandatory', 'is_active_badge', 'subscriber_count', 'created_at')
    list_filter = ('plan_type', 'is_active', 'is_mandatory', 'billing_cycle')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'subscriber_count')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'plan_type', 'description')
        }),
        ('Pricing', {
            'fields': ('base_price', 'billing_cycle')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_mandatory', 'features')
        }),
        ('Metadata', {
            'fields': ('subscriber_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def plan_type_badge(self, obj):
        """Display plan type with color badge"""
        if obj.plan_type == 'base':
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">BASE</span>')
        else:
            return format_html('<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">ADD-ON</span>')
    plan_type_badge.short_description = 'Type'
    
    def base_price_display(self, obj):
        """Display price with currency"""
        return f"${obj.base_price:,.2f}"
    base_price_display.short_description = 'Base Price'
    base_price_display.admin_order_field = 'base_price'
    
    def is_active_badge(self, obj):
        """Display active status with badge"""
        if obj.is_active:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Active</span>')
        else:
            return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">✗ Inactive</span>')
    is_active_badge.short_description = 'Status'
    
    def subscriber_count(self, obj):
        """Count active subscribers"""
        count = obj.user_subscriptions.filter(status='active').count()
        return f"{count} active subscribers"
    subscriber_count.short_description = 'Subscribers'
    
    actions = ['activate_plans', 'deactivate_plans']
    
    def activate_plans(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} subscription plans")
    activate_plans.short_description = 'Activate selected plans'
    
    def deactivate_plans(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} subscription plans")
    deactivate_plans.short_description = 'Deactivate selected plans'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for managing user subscriptions"""
    list_display = ('profile_link', 'plan_name', 'price_display', 'status_badge', 'billing_cycle', 'next_billing_date', 'started_at')
    list_filter = ('status', 'plan__plan_type', 'billing_cycle', 'started_at')
    search_fields = ('profile__first_name', 'profile__last_name', 'profile__email', 'plan__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'started_at', 'ended_at', 'total_revenue')
    fieldsets = (
        ('Subscription Details', {
            'fields': ('id', 'profile', 'plan', 'status')
        }),
        ('Pricing & Billing', {
            'fields': ('price', 'billing_cycle', 'next_billing_date', 'razorpay_subscription_id')
        }),
        ('Timeline', {
            'fields': ('started_at', 'ended_at', 'created_at', 'updated_at')
        }),
        ('Admin', {
            'fields': ('admin_notes', 'total_revenue'),
            'classes': ('collapse',)
        }),
    )
    
    def profile_link(self, obj):
        """Display clickable profile link"""
        profile_name = f"{obj.profile.first_name} {obj.profile.last_name}".strip() or obj.profile.email
        return format_html('<a href="/admin/users/profile/{}/change/">{}</a>', obj.profile.id, profile_name)
    profile_link.short_description = 'User'
    
    def plan_name(self, obj):
        """Display plan name with type badge"""
        if obj.plan.plan_type == 'base':
            badge = '<span style="background-color: #28a745; color: white; padding: 2px 5px; border-radius: 3px; font-size: 10px;">BASE</span>'
        else:
            badge = '<span style="background-color: #007bff; color: white; padding: 2px 5px; border-radius: 3px; font-size: 10px;">ADD-ON</span>'
        return format_html('{} {}', badge, obj.plan.name)
    plan_name.short_description = 'Plan'
    
    def price_display(self, obj):
        """Display price with currency"""
        return f"${obj.price:,.2f}"
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'active': '#28a745',
            'inactive': '#6c757d',
            'pending': '#ffc107',
            'cancelled': '#dc3545',
            'expired': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'
    
    def total_revenue(self, obj):
        """Calculate total revenue from this subscription"""
        total = obj.billing_history.filter(status='success').aggregate(total=Sum('amount'))['total']
        return f"${total:,.2f}" if total else "$0.00"
    total_revenue.short_description = 'Total Revenue'
    
    actions = ['activate_subscriptions', 'cancel_subscriptions', 'mark_pending']
    
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions"""
        count = 0
        for subscription in queryset:
            subscription.activate()
            count += 1
        self.message_user(request, f"Activated {count} subscriptions")
    activate_subscriptions.short_description = 'Activate selected subscriptions'
    
    def cancel_subscriptions(self, request, queryset):
        """Cancel selected subscriptions"""
        count = 0
        for subscription in queryset:
            subscription.cancel()
            count += 1
        self.message_user(request, f"Cancelled {count} subscriptions")
    cancel_subscriptions.short_description = 'Cancel selected subscriptions'
    
    def mark_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f"Marked {updated} subscriptions as pending")
    mark_pending.short_description = 'Mark as pending payment'


@admin.register(BillingHistory)
class BillingHistoryAdmin(admin.ModelAdmin):
    """Admin interface for billing history"""
    list_display = ('profile_name', 'subscription_plan', 'amount_display', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at', 'user_subscription__plan__plan_type')
    search_fields = ('user_subscription__profile__first_name', 'user_subscription__profile__last_name', 'user_subscription__profile__email', 'razorpay_payment_id', 'razorpay_order_id', 'description')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('id', 'user_subscription', 'amount', 'status', 'created_at')
        }),
        ('Payment Information', {
            'fields': ('razorpay_payment_id', 'razorpay_order_id', 'description', 'metadata')
        }),
    )
    
    def profile_name(self, obj):
        """Display user's name"""
        profile = obj.user_subscription.profile
        return f"{profile.first_name} {profile.last_name}".strip() or profile.email
    profile_name.short_description = 'User'
    
    def subscription_plan(self, obj):
        """Display subscription plan name"""
        return obj.user_subscription.plan.name
    subscription_plan.short_description = 'Plan'
    
    def amount_display(self, obj):
        """Display amount with currency"""
        return f"${obj.amount:,.2f}"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'success': '#28a745',
            'pending': '#ffc107',
            'failed': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'
    
    actions = ['export_to_csv']
    
    def export_to_csv(self, request, queryset):
        """Export billing history to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=billing_history.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'User', 'Plan', 'Amount', 'Status', 'Razorpay Payment ID', 'Razorpay Order ID', 'Description'])
        
        for bill in queryset:
            profile = bill.user_subscription.profile
            profile_name = f"{profile.first_name} {profile.last_name}".strip() or profile.email
            writer.writerow([
                bill.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                profile_name,
                bill.user_subscription.plan.name,
                f"${bill.amount:.2f}",
                bill.status,
                bill.razorpay_payment_id or '',
                bill.razorpay_order_id or '',
                bill.description
            ])
        
        return response
    export_to_csv.short_description = 'Export selected to CSV'


# Legacy admin - kept for backward compatibility
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Legacy subscription admin"""
    list_display = ('profile', 'plan', 'status', 'started_at', 'ended_at')
    list_filter = ('status', 'plan')
    search_fields = ('profile__first_name', 'profile__last_name', 'profile__email')
    readonly_fields = ('id', 'started_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show warning message
        self.message_user(request, 'WARNING: This is a legacy model. Please use "User Subscriptions" instead.', level='warning')
        return qs
    
    actions = ['mark_inactive', 'export_selected']

    def mark_inactive(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f"Marked {updated} subscriptions as inactive")
    mark_inactive.short_description = 'Mark selected subscriptions inactive'

    def export_selected(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=subscriptions.csv'
        writer = csv.writer(response)
        writer.writerow(['id', 'profile', 'plan', 'status', 'started_at', 'ended_at'])
        for s in queryset:
            profile_name = f"{s.profile.first_name} {s.profile.last_name}".strip() if s.profile else ''
            writer.writerow([s.id, profile_name, s.plan, s.status, s.started_at, s.ended_at])
        return response
    export_selected.short_description = 'Export selected subscriptions to CSV'
