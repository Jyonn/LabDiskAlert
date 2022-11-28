# Generated by Django 3.1.12 on 2022-11-27 11:40

import SmartDjango.models.fields
import User.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', SmartDjango.models.fields.CharField(max_length=10, unique=True)),
                ('password', SmartDjango.models.fields.CharField(max_length=32)),
                ('admin', models.BooleanField(default=False)),
                ('salt', SmartDjango.models.fields.CharField(max_length=6)),
                ('silent', models.BooleanField(default=False)),
                ('email', models.EmailField(blank=True, max_length=30, null=True)),
                ('email_captcha', SmartDjango.models.fields.CharField(blank=True, max_length=6, null=True)),
                ('email_status', SmartDjango.models.fields.IntegerField(choices=[(0, 'WAIT_BIND'), (1, 'WAIT_CAPTCHA'), (2, 'ACTIVATED')], default=User.models.ChannelStatus['WAIT_BIND'])),
                ('email_silent', models.BooleanField(default=False)),
                ('phone', SmartDjango.models.fields.CharField(blank=True, max_length=20, null=True)),
                ('phone_captcha', SmartDjango.models.fields.CharField(blank=True, max_length=6, null=True)),
                ('phone_status', SmartDjango.models.fields.IntegerField(choices=[(0, 'WAIT_BIND'), (1, 'WAIT_CAPTCHA'), (2, 'ACTIVATED')], default=User.models.ChannelStatus['WAIT_BIND'])),
                ('phone_silent', models.BooleanField(default=False)),
                ('bark', SmartDjango.models.fields.CharField(blank=True, max_length=64, null=True)),
                ('bark_captcha', SmartDjango.models.fields.CharField(blank=True, max_length=6, null=True)),
                ('bark_status', SmartDjango.models.fields.IntegerField(choices=[(0, 'WAIT_BIND'), (1, 'WAIT_CAPTCHA'), (2, 'ACTIVATED')], default=User.models.ChannelStatus['WAIT_BIND'])),
                ('bark_silent', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
                'default_manager_name': 'objects',
            },
        ),
    ]