from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recruiters', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='profile',
            field=models.ForeignKey(help_text='Client candidate profile', on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='users.profile'),
        ),
        migrations.AddConstraint(
            model_name='assignment',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'active')), fields=('profile', 'recruiter'), name='unique_active_assignment_per_recruiter'),
        ),
    ]
