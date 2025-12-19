from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan
from decimal import Decimal


class Command(BaseCommand):
    help = 'Setup initial subscription plans (Base + Add-ons)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Setting up subscription plans...'))
        
        # ============ BASE SUBSCRIPTION ============
        base_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Profile Marketing Services Fee',
            plan_type='base',
            defaults={
                'description': '''
                    Mandatory base subscription for all users. Includes:
                    - Profile visibility on Hyrind platform
                    - Professional profile marketing to recruiters
                    - Access to job listings
                    - Profile optimization tools
                    - Monthly job alerts
                    - Basic support
                ''',
                'base_price': Decimal('400.00'),
                'is_mandatory': True,
                'is_active': True,
                'billing_cycle': 'monthly',
                'features': [
                    'Profile visibility on platform',
                    'Professional profile marketing',
                    'Access to all job listings',
                    'Profile optimization tools',
                    'Monthly job alerts',
                    'Email support',
                ]
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created BASE plan: {base_plan.name} - ${base_plan.base_price}'))
        else:
            self.stdout.write(self.style.WARNING(f'○ BASE plan already exists: {base_plan.name}'))
        
        # ============ ADD-ON SERVICES ============
        
        addon_plans = [
            {
                'name': 'Skill Development Training',
                'description': '''
                    Comprehensive skill development program including:
                    - Technical skills training
                    - Soft skills workshops
                    - Interview preparation
                    - Resume enhancement
                    - Mock interviews
                    - Career coaching sessions
                ''',
                'base_price': Decimal('150.00'),
                'billing_cycle': 'monthly',
                'features': [
                    'Technical skills training',
                    'Soft skills workshops',
                    'Interview preparation',
                    'Resume enhancement',
                    '2 mock interviews per month',
                    'Career coaching sessions',
                ]
            },
            {
                'name': 'Premium Job Matching',
                'description': '''
                    Advanced job matching and placement services:
                    - Priority job matching algorithm
                    - Direct recruiter connections
                    - Exclusive job opportunities
                    - Personalized job recommendations
                    - Application tracking
                ''',
                'base_price': Decimal('200.00'),
                'billing_cycle': 'monthly',
                'features': [
                    'Priority in job matching',
                    'Direct recruiter connections',
                    'Exclusive job opportunities',
                    'Personalized recommendations',
                    'Application tracking dashboard',
                    'Weekly job market insights',
                ]
            },
            {
                'name': 'Career Mentorship Program',
                'description': '''
                    One-on-one mentorship with industry professionals:
                    - Monthly 1-on-1 mentorship sessions
                    - Career roadmap planning
                    - Industry insights
                    - Networking opportunities
                    - Salary negotiation coaching
                ''',
                'base_price': Decimal('250.00'),
                'billing_cycle': 'monthly',
                'features': [
                    'Monthly 1-on-1 mentorship (60 min)',
                    'Personalized career roadmap',
                    'Industry insights and trends',
                    'Networking event access',
                    'Salary negotiation coaching',
                    'LinkedIn profile optimization',
                ]
            },
            {
                'name': 'Certification Assistance',
                'description': '''
                    Support for professional certifications:
                    - Certification guidance
                    - Study materials and resources
                    - Exam preparation support
                    - Certification reimbursement (partial)
                ''',
                'base_price': Decimal('100.00'),
                'billing_cycle': 'monthly',
                'features': [
                    'Certification guidance',
                    'Study materials access',
                    'Exam preparation support',
                    'Certification reimbursement (up to $500/year)',
                    'Study group access',
                ]
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        for addon_data in addon_plans:
            addon, created = SubscriptionPlan.objects.get_or_create(
                name=addon_data['name'],
                plan_type='addon',
                defaults={
                    'description': addon_data['description'],
                    'base_price': addon_data['base_price'],
                    'is_mandatory': False,
                    'is_active': True,
                    'billing_cycle': addon_data['billing_cycle'],
                    'features': addon_data['features'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created ADD-ON: {addon.name} - ${addon.base_price}'))
            else:
                existing_count += 1
                self.stdout.write(self.style.WARNING(f'○ ADD-ON already exists: {addon.name}'))
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Setup Complete!'))
        self.stdout.write(f'  Base Plans: 1')
        self.stdout.write(f'  Add-on Plans: {len(addon_plans)}')
        self.stdout.write(f'  Newly Created: {created_count + (1 if created else 0)}')
        self.stdout.write(f'  Already Existed: {existing_count + (0 if created else 1)}')
        self.stdout.write('='*60)
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Review plans in admin panel: /admin/subscriptions/subscriptionplan/')
        self.stdout.write('2. Customize add-on prices per user as needed')
        self.stdout.write('3. Frontend can now fetch plans from: /api/subscriptions/plans/')
