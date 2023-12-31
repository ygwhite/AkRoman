# Generated by Django 4.1.1 on 2023-06-12 11:03

from django.db import migrations, models
import django.db.models.deletion
import utils.django


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('day', models.IntegerField()),
                ('price', models.IntegerField()),
                ('created_at', models.DateTimeField(default=utils.django.custom_now)),
            ],
        ),
        migrations.CreateModel(
            name='UserSubscriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=utils.django.custom_now)),
                ('subscription_name', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='payments.subscription')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
            ],
        ),
    ]
