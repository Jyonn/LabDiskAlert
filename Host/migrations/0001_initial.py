# Generated by Django 3.1.12 on 2022-11-27 11:40

import SmartDjango.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', SmartDjango.models.fields.CharField(max_length=20, unique=True)),
                ('internal_ip', SmartDjango.models.fields.CharField(max_length=20, unique=True)),
                ('token', SmartDjango.models.fields.CharField(max_length=32)),
                ('alert_percentage', SmartDjango.models.fields.IntegerField(default=80)),
                ('silent', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
                'default_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='HostDisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', SmartDjango.models.fields.CharField(max_length=20)),
                ('listen', models.BooleanField(default=False)),
                ('last_logging_time', SmartDjango.models.fields.DateTimeField(blank=True, null=True)),
                ('last_logging_data', models.TextField(blank=True, null=True)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Host.host')),
            ],
            options={
                'unique_together': {('host', 'name')},
            },
        ),
        migrations.CreateModel(
            name='DiskUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bind', models.BooleanField(default=True)),
                ('alert_percentage', SmartDjango.models.fields.IntegerField(default=5)),
                ('disk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Host.hostdisk')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='User.user')),
            ],
            options={
                'unique_together': {('disk', 'user')},
            },
        ),
    ]
