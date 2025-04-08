# Generated by Django 5.1.1 on 2025-04-01 14:42

from django.db import migrations, models
import django.db.models.deletion


def clear_subscription_data(apps, schema_editor):
    Subscription = apps.get_model('healthxpfront', 'Subscription')
    Subscription.objects.all().delete()


def reverse_clear_subscription_data(apps, schema_editor):
    pass  # We can't restore deleted data


class Migration(migrations.Migration):

    dependencies = [
        ('healthxpfront', '0007_category_order_product_orderitem'),
    ]

    operations = [
        migrations.RunPython(clear_subscription_data,
                             reverse_clear_subscription_data),
        migrations.CreateModel(
            name='SubscriptionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField()),
                ('amount', models.DecimalField(decimal_places=2,
                 help_text='Monthly subscription amount in USD', max_digits=10)),
                ('features', models.TextField(
                    help_text='List of features included in this subscription type')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['amount'],
            },
        ),
        migrations.AlterField(
            model_name='subscription',
            name='subscription_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    related_name='subscriptions', to='healthxpfront.subscriptiontype'),
        ),
    ]
