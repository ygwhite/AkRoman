# Generated by Django 4.1.1 on 2023-06-12 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='currencypair',
            name='is_published',
            field=models.BooleanField(default=True, verbose_name='Показывать пары'),
        ),
    ]
