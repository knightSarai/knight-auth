# Generated by Django 4.2.4 on 2023-08-12 15:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('digest', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('token_key', models.CharField(db_index=True, max_length=25)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expiry', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'swappable': 'KNOX_TOKEN_MODEL',
            },
        ),
    ]
