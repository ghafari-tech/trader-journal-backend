from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_badge', '0001_initial'),
        ('app_user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='badge',
            options={'ordering': ['order', 'id']},
        ),
        migrations.RemoveField(
            model_name='badge',
            name='acquisition_by',
        ),
        migrations.AddField(
            model_name='badge',
            name='icon',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='badge',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='badge',
            name='trigger_count',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='badge',
            name='trigger_type',
            field=models.CharField(
                choices=[
                    ('plan_streak', 'روزهای متوالی پایبند به پلن'),
                    ('drawdown_reduction', 'کاهش دراودان'),
                    ('no_revenge_trade', 'روزهای بدون Revenge Trade'),
                    ('trade_count', 'تعداد معاملات'),
                    ('profit_factor', 'Profit Factor'),
                    ('no_emotional_entry', 'روزهای بدون ورود احساسی'),
                    ('first_trade', 'اولین معامله'),
                    ('journal_streak', 'روزهای متوالی ژورنال‌نویسی'),
                    ('profitable_month', 'ماه سودده'),
                    ('win_rate', 'Win Rate'),
                    ('risk_management', 'مدیریت ریسک'),
                    ('no_overtrading', 'بدون Overtrading'),
                    ('capital_double', 'دابل کردن سرمایه'),
                    ('a_plus_streak', 'معاملات A+ متوالی'),
                    ('mt_connection', 'اتصال متاتریدر'),
                    ('checklist_master', 'استاد چک‌لیست'),
                ],
                default='first_trade',
                max_length=50,
            ),
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_finished', models.BooleanField(default=False)),
                ('progress', models.PositiveIntegerField(default=0)),
                ('last_progress_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_badges', to='app_badge.badge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_badges', to='app_user.user')),
            ],
            options={
                'unique_together': {('user', 'badge')},
            },
        ),
    ]