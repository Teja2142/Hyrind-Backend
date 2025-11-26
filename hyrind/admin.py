from django.urls import path
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

class DashboardAdmin(admin.AdminSite):
    site_header = 'Hyrind Admin'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        from onboarding.models import Onboarding
        from subscriptions.models import Subscription
        from recruiters.models import Assignment
        from audit.models import AuditLog
        onboarded = Onboarding.objects.filter(completed=True).count()
        active_subs = Subscription.objects.filter(status='active').count()
        assignments = Assignment.objects.count()
        recent_audit = AuditLog.objects.order_by('-timestamp')[:10]
        context = dict(
            self.each_context(request),
            onboarded=onboarded,
            active_subs=active_subs,
            assignments=assignments,
            recent_audit=recent_audit,
        )
        return TemplateResponse(request, "admin/dashboard.html", context)

admin_site = DashboardAdmin()
# Mirror registered apps/models from default admin.site to our custom admin_site
for model, model_admin in admin.site._registry.items():
    try:
        admin_site.register(model, type(model_admin))
    except Exception:
        # already registered or registration failed; ignore
        pass
