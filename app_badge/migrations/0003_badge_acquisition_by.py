from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_badge', '0002_badge_new_fields'),
        ('app_user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='acquisition_by',
            field=models.ManyToManyField(
                blank=True,
                related_name='badges',
                through='app_badge.UserBadge',
                to='app_user.user',
            ),
        ),
    ]