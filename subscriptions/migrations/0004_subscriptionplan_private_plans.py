from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_rename_stripe_subscription_id_subscription_razorpay_subscription_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='is_private',
            field=models.BooleanField(default=False, help_text='If true, this plan is only visible to explicitly allowed profiles'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='allowed_profiles',
            field=models.ManyToManyField(blank=True, help_text='Profiles that can view this private plan', related_name='private_addon_plans', to='users.profile'),
        ),
    ]
