from django.urls import path
from . import views

urlpatterns = [
    # ── Subscription Plan Templates (Admin) ───────────────────────────────
    path('plans/',                          views.subscription_plan_list,     name='billing-plan-list'),
    path('plans/create/',                   views.create_subscription_plan,   name='billing-plan-create'),
    path('plans/<uuid:plan_id>/',           views.update_subscription_plan,   name='billing-plan-update'),
    path('plans/<uuid:plan_id>/apply/',     views.apply_subscription_plan,    name='billing-plan-apply'),

    # ── Candidate-scoped endpoints ─────────────────────────────────────────
    # Subscriptions
    path('<uuid:candidate_id>/subscription/',         views.get_subscription,    name='billing-subscription-get'),
    path('<uuid:candidate_id>/subscription/create/',  views.create_subscription, name='billing-subscription-create'),
    path('<uuid:candidate_id>/subscription/update/',  views.update_subscription, name='billing-subscription-update'),

    # Payment line items
    path('<uuid:candidate_id>/items/',                views.payment_items,       name='billing-items'),
    path('<uuid:candidate_id>/items/create/',         views.create_payment_item, name='billing-item-create'),
    path('<uuid:candidate_id>/items/<uuid:item_id>/', views.update_payment_item, name='billing-item-update'),

    # Payments — record uses candidate-scoped path to match frontend
    path('<uuid:candidate_id>/payments/',                                   views.payment_history,          name='billing-payment-history'),
    path('<uuid:candidate_id>/payments/record/',                            views.record_payment_scoped,    name='billing-record-payment'),
    path('<uuid:candidate_id>/payments/<uuid:payment_id>/receipt/',         views.payment_receipt_download, name='billing-payment-receipt'),

    # Invoices
    path('<uuid:candidate_id>/invoices/',             views.invoice_list,        name='billing-invoices'),

    # ── Razorpay Gateway ─────────────────────────────────────────────────────
    path('<uuid:candidate_id>/razorpay/create-order/', views.create_razorpay_order,    name='razorpay-create-order'),
    path('<uuid:candidate_id>/razorpay/verify/',        views.verify_razorpay_payment, name='razorpay-verify'),
    path('razorpay/webhook/',                           views.razorpay_webhook,        name='razorpay-webhook'),
]
